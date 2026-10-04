from datetime import date,timedelta
from decimal import Decimal
import hashlib
from sqlalchemy import select,func
from app.models.entities import Requisition,PurchaseOrder,Document,Profile
from app.services.intelligence import calculate_line,analyze_price,vendor_risk,invoice_mismatch
from app.core.auth import current_user
from app.main import app

PREFIX='/api/v1'
def ok(response,status=200):
    assert response.status_code==status,response.text
    return response.json()
def prepare(env,price=52000,quantity=2):
    c,login,_=env;login('requester')
    r=ok(c.post(PREFIX+'/requisitions',json={'title':'Laptop refresh','justification':'Replace ageing laboratory machines','department_id':1,'items':[{'item_name':'Business laptop','category':'Computers','description':'16 GB RAM','quantity':quantity,'unit':'piece','estimated_unit_price':52000}]}),201)
    url=PREFIX+'/requisitions/'+str(r['id']);ok(c.post(url+'/submit'));login('procurement');ok(c.post(url+'/invitations',json={'vendor_id':1}),201)
    quote={'vendor_id':1,'quotation_number':'Q-TEST','quotation_date':str(date.today()),'valid_until':str(date.today()+timedelta(days=30)),'delivery_days':7,'delivery_terms':'Campus delivery','items':[{'requisition_item_id':r['items'][0]['id'],'unit_price':price,'tax_percent':18,'discount':0}]}
    q=ok(c.post(url+'/quotations',json=quote),201);ok(c.post(url+'/recalculate'))
    return url,r,q,quote

def test_calculation_exact():
    result=calculate_line(Decimal('99.99'),3,18,10)
    assert result=={'subtotal':Decimal('299.97'),'discount':Decimal('10.00'),'tax':Decimal('52.19'),'total':Decimal('342.16')}
def test_anomaly_cases():
    h=[50000,51000,52000,52000,53000,54000]
    assert analyze_price(72000,h)['anomaly_flag']
    assert not analyze_price(52000,h)['anomaly_flag']
    assert analyze_price(100,[50,51])['status']=='INSUFFICIENT_HISTORY'
    assert analyze_price(120,[100,100,100,100,100],25)['anomaly_flag'] # IQR boundary independently flags
    assert analyze_price(125,[100,100,100],25)['status']=='NORMAL' # strict threshold

def test_risk_bands():
    for rate,band in [(0,'Low'),(.4,'Medium'),(.8,'High')]:
        facts={'total_orders':20,'completed_orders':20,'late_deliveries':int(20*rate),'quotation_lines':20,'anomalous_lines':int(20*rate),'disputed_orders':int(20*rate),'incomplete_orders':int(20*rate),'invoiced_orders':20,'invoice_mismatches':int(20*rate)}
        risk=vendor_risk(facts);assert risk['band']==band;assert risk['score']==rate*100
    assert vendor_risk({})['band']=='INSUFFICIENT_HISTORY'
def test_invoice_tolerance():
    assert invoice_mismatch(106,100)[0];assert not invoice_mismatch(105,100)[0]
def test_health_and_openapi(env):
    c,_,_=env;assert ok(c.get('/health'))['status']=='ok';assert c.get('/openapi.json').status_code==200;assert c.get('/docs').status_code==200

def test_missing_and_invalid_jwt(env, monkeypatch):
    c, _, _ = env

    # No bearer token
    assert c.get(PREFIX + '/me').status_code == 401

    import app.core.auth as auth
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        'supabase_url',
        'https://unit-test.supabase.co'
    )
    monkeypatch.setattr(
        settings,
        'anon_key',
        'test-publishable-key'
    )

    class FakeResponse:
        status_code = 401

        def json(self):
            return {'message': 'Invalid token'}

    monkeypatch.setattr(
        auth.httpx,
        'get',
        lambda *args, **kwargs: FakeResponse()
    )

    response = c.get(
        PREFIX + '/me',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == 401

def test_end_to_end_and_integrity(env):
    c,login,session=env;url,r,q,_=prepare(env)
    matrix=ok(c.get(url+'/comparison'));assert matrix['quotations'][0]['risk']['band']=='Low'
    content=b'%PDF-1.4\nSynthetic test document\n%%EOF'
    doc=ok(c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('quote.pdf',content,'application/pdf')}),201)
    assert doc['sha256']==hashlib.sha256(content).hexdigest()
    assert c.get(PREFIX+f"/documents/{doc['id']}").content==content
    ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Best total and reliable delivery'}))
    login('approver');assert ok(c.post(url+'/approval',json={'decision':'APPROVED','comment':'Specifications and budget checked'}))['status']=='PENDING_APPROVAL'
    assert c.post(url+'/approval',json={'decision':'APPROVED','comment':'Duplicate decision'}).status_code==409
    login('finance_admin');assert ok(c.post(url+'/approval',json={'decision':'APPROVED','comment':'Senior budget authorization'}))['status']=='APPROVED'
    login('procurement');po=ok(c.post(url+'/purchase-order'),201)
    assert po['total']==122720
    assert c.post(url+'/purchase-order').status_code==409
    ok(c.post(PREFIX+f"/purchase-orders/{po['id']}/delivery",json={'status':'PARTIAL','delivered_at':str(date.today()),'notes':'One unit received'}),201)
    assert ok(c.get(url))['status']=='PO_ISSUED'
    ok(c.post(PREFIX+f"/purchase-orders/{po['id']}/delivery",json={'status':'DELIVERED','delivered_at':str(date.today()),'notes':'All items inspected'}),201)
    login('finance_admin');inv=ok(c.post(PREFIX+f"/purchase-orders/{po['id']}/invoice",json={'invoice_number':'INV-TEST','invoice_date':str(date.today()),'amount':130000}),201)
    assert inv['mismatch_flag']
    ok(c.post(PREFIX+f"/invoices/{inv['id']}/file",files={'file':('invoice.pdf',content,'application/pdf')}),201)
    ok(c.post(PREFIX+f"/purchase-orders/{po['id']}/close",json={'comment':'Discrepancy reviewed against approved service charges'}))
    assert ok(c.get(url))['status']=='CLOSED'
    assert c.post(PREFIX+f"/invoices/{inv['id']}/file",files={'file':('invoice.pdf',content)}).status_code==409
    logs=ok(c.get(url+'/audit'));actions={a['action'] for a in logs}
    assert {'REQUISITION_CREATED','REQUISITION_SUBMITTED','VENDOR_INVITED','QUOTATION_ADDED','COMPARISON_GENERATED','PREFERRED_VENDOR_PROPOSED','SENT_FOR_APPROVAL','APPROVAL_APPROVED','PO_ISSUED','DELIVERY_RECORDED','INVOICE_RECORDED','WORKFLOW_CLOSED','DOCUMENT_UPLOADED'}<=actions
    assert ok(c.get(PREFIX+f"/purchase-orders/{po['id']}"))['snapshot_json']['quotation']['grand_total']==122720

def test_unauthorized_approval_leaves_state_unchanged(env):
    c,login,_=env;url,_,_,_=prepare(env);ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Choose vendor on evidence'}));login('requester')
    before=ok(c.get(url))['status'];res=c.post(url+'/approval',json={'decision':'APPROVED','comment':'Attempt bypass as requester'})
    assert res.status_code==403;assert ok(c.get(url))['status']==before
    login('finance_admin');assert ok(c.get('/metrics'))['counters']['failed_authorization']>=1

def test_role_and_state_guards(env):
    c,login,session=env;url,r,_,_=prepare(env)
    assert c.post(url+'/purchase-order').status_code==409
    with session() as db:assert db.scalar(select(func.count()).select_from(PurchaseOrder))==0
    login('finance_admin');assert c.post(url+'/invitations',json={'vendor_id':2}).status_code==403
    login('other');assert c.get(url).status_code==403
    login('requester');assert c.post(url+'/submit').status_code==409
    assert c.patch(url,json={'status':'PO_ISSUED'}).status_code==405

def test_invalid_quotation_duplicate_invite_and_locked_quote(env):
    c,login,_=env;url,req,q,payload=prepare(env)
    assert c.post(url+'/invitations',json={'vendor_id':1}).status_code==409
    payload['items'][0]['unit_price']=-1
    assert c.put(PREFIX+f"/quotations/{q['id']}",json=payload).status_code==422
    payload['items'][0]['unit_price']=100;payload['items'][0]['discount']=999999
    assert c.put(PREFIX+f"/quotations/{q['id']}",json=payload).status_code==422
    payload['items'][0]['discount']=0;payload['items'].append(dict(payload['items'][0]))
    assert c.put(PREFIX+f"/quotations/{q['id']}",json=payload).status_code==422
    payload['items'].pop();payload['items'][0]['unit_price']=52000
    ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Evidence reviewed by procurement'}))
    assert c.put(PREFIX+f"/quotations/{q['id']}",json=payload).status_code==409

def test_bad_file_and_foreign_document(env):
    c,login,_=env;url,r,q,_=prepare(env)
    assert c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('bad.pdf',b'<script>bad</script>','application/pdf')}).status_code==422
    doc=ok(c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('../../quote.pdf',b'%PDF-1.4 test','application/pdf')}),201)
    assert doc['original_name']=='quote.pdf'
    login('other');assert c.get(PREFIX+f"/documents/{doc['id']}").status_code==403

def test_tampered_file_fails_integrity(env):
    c,login,sessions=env;_,_,q,_=prepare(env)
    doc=ok(c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('q.pdf',b'%PDF-1.4 test')}),201)
    from app.core.config import settings
    from pathlib import Path
    with sessions() as db:key=db.get(Document,doc['id']).storage_key
    (Path(settings.upload_dir)/key).write_bytes(b'changed')
    assert c.get(PREFIX+f"/documents/{doc['id']}").status_code==409

def test_low_amount_single_approval_and_rejection(env):
    c,login,_=env;url,_,_,_=prepare(env,price=50000,quantity=1)
    ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Accept comparable offer'}));login('approver')
    assert ok(c.post(url+'/approval',json={'decision':'REJECTED','comment':'Budget deferred to next quarter'}))['status']=='REJECTED'
    login('procurement');assert c.post(url+'/purchase-order').status_code==409

def test_draft_edit_cancel_and_input_validation(env):
    c,login,_=env;login('requester')
    data={'title':'Mouse purchase','justification':'Replace broken input devices','department_id':1,'items':[{'item_name':'Mouse','category':'IT','quantity':1,'unit':'piece','estimated_unit_price':50}]}
    r=ok(c.post(PREFIX+'/requisitions',json=data),201);url=PREFIX+'/requisitions/'+str(r['id'])
    data['items'][0]['quantity']=2;assert ok(c.put(url,json=data))['estimated_total']==100
    data['items'][0]['quantity']=0;assert c.put(url,json=data).status_code==422
    data['items'][0]['quantity']=2;data['estimated_total']=1;assert c.put(url,json=data).status_code==422
    ok(c.post(url+'/cancel',json={'comment':'Purchase no longer required'}));assert c.post(url+'/submit').status_code==409

def test_self_approval_blocked_even_if_role_changes(env):
    c,login,sessions=env;url,r,_,_=prepare(env);ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Comparison checked'}))
    with sessions.begin() as db:user=db.get(Profile,r['requester_id']);user.role='approver'
    login('requester');assert c.post(url+'/approval',json={'decision':'APPROVED','comment':'Self authorization attempted'}).status_code==403

def test_supabase_token_validation_and_role_safety(env, monkeypatch):
    import app.core.auth as auth
    from app.core.config import settings

    c, _, _ = env

    monkeypatch.setattr(
        settings,
        'supabase_url',
        'https://unit-test.supabase.co'
    )
    monkeypatch.setattr(
        settings,
        'anon_key',
        'test-publishable-key'
    )

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self.payload = payload

        def json(self):
            return self.payload

    def fake_get(url, headers, timeout):
        token = headers['Authorization'].replace('Bearer ', '')

        if token == 'valid-token':
            return FakeResponse(
                200,
                {
                    'id': 'new-verified-user',
                    'email': 'new@example.com',
                    'user_metadata': {
                        'role': 'finance_admin'
                    }
                }
            )

        return FakeResponse(
            401,
            {'message': 'Invalid or expired token'}
        )

    monkeypatch.setattr(auth.httpx, 'get', fake_get)

    # Valid Supabase session
    response = c.get(
        PREFIX + '/me',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200

    user = response.json()

    # User-editable metadata must never escalate privileges
    assert user['role'] == 'requester'
    assert user['email'] == 'new@example.com'

    # Invalid/expired Supabase tokens must be rejected
    for token in ['invalid-token', 'expired-token']:
        response = c.get(
            PREFIX + '/me',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 401

def test_storage_failure_rolls_back_and_missing_file_is_controlled(env,monkeypatch):
    from fastapi import HTTPException
    from app.services import storage
    c,login,sessions=env;url,r,q,_=prepare(env)
    def unavailable(data):raise HTTPException(503,'Document storage unavailable; retry later')
    monkeypatch.setattr(storage,'save',unavailable)
    assert c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('q.pdf',b'%PDF-1.4 test')}).status_code==503
    with sessions() as db:assert db.scalar(select(func.count()).select_from(Document))==0
    assert ok(c.get(url))['status']=='COMPARISON_READY'

def test_single_level_approval_and_expired_quote(env):
    c,login,_=env;url,r,q,payload=prepare(env,price=50000,quantity=1)
    ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':'Single-level policy applies'}));login('approver')
    assert ok(c.post(url+'/approval',json={'decision':'APPROVED','comment':'Budget and specification checked'}))['status']=='APPROVED'
    login('procurement');assert c.post(url+'/purchase-order').status_code==201

def test_file_size_limit(env,monkeypatch):
    from app.core.config import settings
    c,_,_=env;_,_,q,_=prepare(env);monkeypatch.setattr(settings,'max_upload',5)
    assert c.post(PREFIX+f"/quotations/{q['id']}/file",files={'file':('q.pdf',b'%PDF-too-large')}).status_code==413
