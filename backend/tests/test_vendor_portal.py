from datetime import date,timedelta
from sqlalchemy import select
from app.models.entities import VendorHistory,Vendor

PREFIX='/api/v1'

def ok(response,status=200):
    assert response.status_code==status,response.text
    return response.json()

def test_vendor_portal_rfq_to_procurement_flow(env):
    c,login,sessions=env
    login('requester')
    me=ok(c.get(PREFIX+'/me'))
    req=ok(c.post(PREFIX+'/requisitions',json={
        'title':'Vendor portal laptop RFQ',
        'justification':'Need comparable supplier quotations for a controlled sourcing exercise.',
        'department_id':me['department_id'],
        'items':[{'item_name':'Business laptop','category':'Computers','description':'16 GB RAM, 512 GB SSD','quantity':2,'unit':'piece','estimated_unit_price':52000}],
    }),201)
    url=PREFIX+f"/requisitions/{req['id']}"
    ok(c.post(url+'/submit'))

    login('procurement')
    broadcast=ok(c.post(url+'/invite-all'))
    assert len(broadcast['invitations'])>=3

    login('vendor')
    assert c.get(PREFIX+'/requisitions').status_code==403
    inbox=ok(c.get(PREFIX+'/vendor/rfqs'))
    entry=next(x for x in inbox if x['requisition']['id']==req['id'])
    assert entry['can_submit'] is True
    assert entry['quotation'] is None

    quote=ok(c.post(PREFIX+f"/vendor/rfqs/{req['id']}/quotation",json={
        'quotation_number':'VP-Q-001',
        'quotation_date':str(date.today()),
        'valid_until':str(date.today()+timedelta(days=30)),
        'delivery_days':8,
        'delivery_terms':'Campus delivery with one-year warranty',
        'items':[{'requisition_item_id':entry['items'][0]['id'],'unit_price':51000,'tax_percent':18,'discount':0}],
    }),201)
    assert quote['vendor']['email']=='vendor@example.com'

    # A vendor cannot submit twice and cannot see staff comparison endpoints.
    assert c.post(PREFIX+f"/vendor/rfqs/{req['id']}/quotation",json={
        'quotation_number':'VP-Q-002','quotation_date':str(date.today()),'valid_until':None,
        'delivery_days':8,'delivery_terms':'duplicate',
        'items':[{'requisition_item_id':entry['items'][0]['id'],'unit_price':50000,'tax_percent':18,'discount':0}],
    }).status_code==409
    assert c.get(url+'/comparison').status_code==403

    login('procurement')
    detail=ok(c.get(url))
    assert any(q['id']==quote['id'] for q in detail['quotations'])


def test_new_vendor_history_is_neutral(env):
    c,login,sessions=env
    with sessions.begin() as db:
        vendor=Vendor(name='Brand New Supplier',email='new-supplier@example.com',contact='New')
        db.add(vendor);db.flush();vendor_id=vendor.id
        db.add(VendorHistory(vendor_id=vendor_id))
    login('procurement')
    risk=ok(c.get(PREFIX+f'/vendors/{vendor_id}/risk'))
    assert risk['score'] is None
    assert risk['band']=='NEW_VENDOR'

def test_established_vendor_can_be_scored_with_partial_factor_coverage():
    from app.services.intelligence import vendor_risk
    risk=vendor_risk({
        'total_orders':12,'completed_orders':11,'late_deliveries':1,
        'quotation_lines':20,'anomalous_lines':2,'disputed_orders':1,
        'incomplete_orders':1,'invoiced_orders':0,'invoice_mismatches':0,
    })
    assert risk['score'] is not None
    assert risk['history_status']=='ESTABLISHED'
    assert risk['coverage_percent']==90


def test_partial_delivery_accepts_future_expected_completion():
    from app.schemas.contracts import DeliveryIn
    payload=DeliveryIn(
        status='PARTIAL',
        delivered_at=date.today(),
        expected_completion_at=date.today()+timedelta(days=5),
        notes='Two units received; balance is scheduled.',
    )
    assert payload.expected_completion_at==date.today()+timedelta(days=5)


def test_approval_inbox_contains_vendor_reason_and_final_rfq_status(env):
    c,login,_=env
    login('requester')
    me=ok(c.get(PREFIX+'/me'))
    req=ok(c.post(PREFIX+'/requisitions',json={
        'title':'Approval context test',
        'justification':'Verify vendor selection evidence is visible to approvers.',
        'department_id':me['department_id'],
        'items':[{'item_name':'Business laptop','category':'Computers','description':'16 GB RAM','quantity':2,'unit':'piece','estimated_unit_price':52000}],
    }),201)
    url=PREFIX+f"/requisitions/{req['id']}"
    ok(c.post(url+'/submit'))
    login('procurement');ok(c.post(url+'/invite-all'))
    login('vendor')
    entry=next(x for x in ok(c.get(PREFIX+'/vendor/rfqs')) if x['requisition']['id']==req['id'])
    ok(c.post(PREFIX+f"/vendor/rfqs/{req['id']}/quotation",json={
        'quotation_number':'APP-Q-1','quotation_date':str(date.today()),
        'valid_until':str(date.today()+timedelta(days=30)),'delivery_days':5,
        'delivery_terms':'Five business days',
        'items':[{'requisition_item_id':entry['items'][0]['id'],'unit_price':52000,'tax_percent':18,'discount':0}],
    }),201)
    login('procurement');ok(c.post(url+'/recalculate'))
    reason='Best balance of price, delivery commitment and historical performance.'
    ok(c.post(url+'/send-for-approval',json={'vendor_id':1,'comment':reason}))
    login('approver')
    inbox=ok(c.get(PREFIX+'/approvals/inbox'))
    item=next(x for x in inbox if x['id']==req['id'])
    assert item['preferred_vendor']['id']==1
    assert item['selection_reason']==reason
    assert item['selected_quotation']['quotation_number']=='APP-Q-1'
    assert next(i for i in item['invitations'] if i['vendor_id']==1)['status']=='SELECTED_FOR_APPROVAL'
    ok(c.post(url+'/approval',json={'decision':'APPROVED','comment':'Technical and sourcing evidence checked.'}))
    login('finance_admin')
    ok(c.post(url+'/approval',json={'decision':'APPROVED','comment':'Budget authorization completed.'}))
    login('procurement')
    final=ok(c.get(url))
    assert next(i for i in final['invitations'] if i['vendor_id']==1)['status']=='APPROVED'
