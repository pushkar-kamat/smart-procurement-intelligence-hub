from datetime import date
from uuid import uuid4
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import current_user, roles
from app.core.config import settings
from app.models.entities import *
from app.schemas.contracts import *
from app.services.workflow import *
from app.services import storage
router=APIRouter(prefix='/api/v1')
DB=Depends(get_db,scope="function")
USER=Depends(current_user)
PROC=Depends(roles('procurement'))
FIN=Depends(roles('finance_admin'))
REQ=Depends(roles('requester'))

from app.services.intelligence import money, calculate_line, analyze_price, invoice_mismatch

@router.get('/me')
def me(user=USER): return row(user)

@router.get('/departments')
def departments(db:Session=DB,user=USER): return [row(x) for x in db.scalars(select(Department).order_by(Department.name))]

@router.get('/profiles')
def profiles(db:Session=DB,user=FIN): return [row(x) for x in db.scalars(select(Profile))]

@router.patch('/profiles/{id}')
def update_profile(id:int,data:ProfileUpdate,db:Session=DB,user=FIN):
    if id==user.id: raise HTTPException(409,'Another administrator must change your account')
    p=fetch(db,Profile,id)
    if data.department_id: fetch(db,Department,data.department_id)
    for k,v in data.model_dump().items(): setattr(p,k,v)
    audit(db,user,'PROFILE_UPDATED',entity=p,details=data.model_dump());db.flush();return row(p)

@router.get('/approval-rules')
def approval_rules(db:Session=DB,user=USER): return [row(x) for x in db.scalars(select(ApprovalRule).where(ApprovalRule.active==True).order_by(ApprovalRule.level))]

@router.get('/requisitions')
def requisitions(db:Session=DB,user=USER):
    query=select(Requisition).order_by(Requisition.created_at.desc())
    if user.role=='requester': query=query.where(Requisition.requester_id==user.id)
    return [row(x) for x in db.scalars(query.limit(500))]

def write_items(db,req,items):
    total=Decimal('0')
    for item in items:
        amount=money(item.quantity*item.estimated_unit_price);total+=amount
        db.add(RequisitionItem(requisition_id=req.id,estimated_line_total=amount,**item.model_dump()))
    req.estimated_total=money(total)

@router.post('/requisitions',status_code=201)
def create_requisition(data:RequisitionIn,db:Session=DB,user=REQ):
    fetch(db,Department,data.department_id)
    if user.department_id and user.department_id!=data.department_id: raise HTTPException(403,'Use your assigned department')
    req=Requisition(requester_id=user.id,estimated_total=0,**data.model_dump(exclude={'items'}));db.add(req);db.flush()
    write_items(db,req,data.items);audit(db,user,'REQUISITION_CREATED',req);db.flush();return detail(db,req)

@router.get('/requisitions/{id}')
def get_requisition(id:int,db:Session=DB,user=USER): return detail(db,request_for(db,id,user))

@router.put('/requisitions/{id}')
def edit_requisition(id:int,data:RequisitionIn,db:Session=DB,user=REQ):
    req=request_for(db,id,user,True);state(req,'DRAFT');fetch(db,Department,data.department_id)
    if user.department_id and user.department_id!=data.department_id: raise HTTPException(403,'Use your assigned department')
    for k,v in data.model_dump(exclude={'items'}).items():setattr(req,k,v)
    db.execute(delete(RequisitionItem).where(RequisitionItem.requisition_id==id));write_items(db,req,data.items)
    audit(db,user,'REQUISITION_EDITED',req);db.flush();return detail(db,req)

@router.post('/requisitions/{id}/submit')
def submit(id:int,db:Session=DB,user=REQ):
    req=request_for(db,id,user,True);state(req,'DRAFT')
    if req.estimated_total<=0:raise HTTPException(422,'At least one valid line item is required')
    req.status='SUBMITTED';req.submitted_at=now();audit(db,user,'REQUISITION_SUBMITTED',req);return row(req)

@router.post('/requisitions/{id}/cancel')
def cancel(id:int,data:CommentIn,db:Session=DB,user=REQ):
    req=request_for(db,id,user,True);state(req,'DRAFT','SUBMITTED');req.status='CANCELLED';audit(db,user,'REQUISITION_CANCELLED',req,details=data.model_dump());return row(req)

@router.get('/vendors')
def vendors(db:Session=DB,user=USER): return [row(x) for x in db.scalars(select(Vendor).order_by(Vendor.name))]

@router.post('/vendors',status_code=201)
def create_vendor(data:VendorIn,db:Session=DB,user=PROC):
    v=Vendor(**data.model_dump());db.add(v);db.flush();audit(db,user,'VENDOR_CREATED',entity=v);return row(v)

@router.put('/vendors/{id}')
def update_vendor(id:int,data:VendorIn,db:Session=DB,user=PROC):
    v=fetch(db,Vendor,id)
    for k,value in data.model_dump().items():setattr(v,k,value)
    audit(db,user,'VENDOR_UPDATED',entity=v,details={'active':v.active});return row(v)

@router.get('/requisitions/{id}/invitations')
def invitations(id:int,db:Session=DB,user=USER):return detail(db,request_for(db,id,user))['invitations']

@router.post('/requisitions/{id}/invitations',status_code=201)
def invite(id:int,data:InviteIn,db:Session=DB,user=PROC):
    req=request_for(db,id,user,True);state(req,'SUBMITTED','SOURCING','QUOTATIONS_RECEIVED')
    v=fetch(db,Vendor,data.vendor_id)
    if not v.active:raise HTTPException(409,'Vendor is inactive')
    if db.scalar(select(Invitation).where(Invitation.requisition_id==id,Invitation.vendor_id==v.id)):raise HTTPException(409,'Vendor already invited')
    i=Invitation(requisition_id=id,vendor_id=v.id);db.add(i)
    if req.status=='SUBMITTED':req.status='SOURCING'
    audit(db,user,'VENDOR_INVITED',req,details={'vendor_id':v.id});db.flush();return row(i)

def set_quote(db,req,q,data):
    items={x.id:x for x in db.scalars(select(RequisitionItem).where(RequisitionItem.requisition_id==req.id))}
    if len(data.items)!=len(items) or {x.requisition_item_id for x in data.items}!=set(items):raise HTTPException(422,'Quote must cover each requisition item exactly once')
    for k,v in data.model_dump(exclude={'items'}).items():setattr(q,k,v)
    q.subtotal=q.tax_total=q.discount_total=q.grand_total=Decimal('0')
    db.add(q);db.flush()
    db.execute(delete(QuotationItem).where(QuotationItem.quotation_id==q.id))
    for line in data.items:
        item=items[line.requisition_item_id]
        try: values=calculate_line(line.unit_price,item.quantity,line.tax_percent,line.discount)
        except ValueError as e: raise HTTPException(422,str(e))
        history=list(db.scalars(select(PriceHistory.unit_price).where(PriceHistory.item_name==item.item_name,PriceHistory.unit==item.unit,PriceHistory.observed_at<=data.quotation_date)))
        analysis=analyze_price(line.unit_price,history)
        db.add(QuotationItem(quotation_id=q.id,requisition_item_id=item.id,unit_price=line.unit_price,quantity=item.quantity,tax=values['tax'],discount=values['discount'],line_total=values['total'],analysis=analysis))
        q.subtotal+=values['subtotal'];q.tax_total+=values['tax'];q.discount_total+=values['discount'];q.grand_total+=values['total']
    db.flush()

@router.post('/requisitions/{id}/quotations',status_code=201)
def quotation(id:int,data:QuoteIn,db:Session=DB,user=PROC):
    req=request_for(db,id,user,True);state(req,'SOURCING','QUOTATIONS_RECEIVED','COMPARISON_READY')
    v=fetch(db,Vendor,data.vendor_id)
    if not v.active:raise HTTPException(409,'Vendor is inactive')
    invitation=db.scalar(select(Invitation).where(Invitation.requisition_id==id,Invitation.vendor_id==v.id))
    if not invitation:raise HTTPException(409,'Invite this vendor first')
    if db.scalar(select(Quotation).where(Quotation.requisition_id==id,Quotation.vendor_id==v.id)):raise HTTPException(409,'Vendor quote already exists; edit it instead')
    q=Quotation(requisition_id=id);set_quote(db,req,q,data)
    invitation.status='RESPONDED';invitation.response_at=now();req.status='QUOTATIONS_RECEIVED'
    audit(db,user,'QUOTATION_ADDED',req,details={'quotation_id':q.id,'total':float(q.grand_total)});return quote_view(db,q)

@router.put('/quotations/{id}')
def edit_quote(id:int,data:QuoteIn,db:Session=DB,user=PROC):
    q=fetch(db,Quotation,id);req=request_for(db,q.requisition_id,user,True);state(req,'QUOTATIONS_RECEIVED','COMPARISON_READY')
    if q.vendor_id!=data.vendor_id:raise HTTPException(422,'Vendor cannot be changed')
    set_quote(db,req,q,data);req.status='QUOTATIONS_RECEIVED';audit(db,user,'QUOTATION_UPDATED',req,details={'quotation_id':id});return quote_view(db,q)

@router.get('/requisitions/{id}/quotations')
def quotes(id:int,db:Session=DB,user=USER):return detail(db,request_for(db,id,user))['quotations']

@router.get('/quotations/{id}')
def quote_detail(id:int,db:Session=DB,user=USER):
    q=fetch(db,Quotation,id);request_for(db,q.requisition_id,user);return quote_view(db,q)

@router.post('/requisitions/{id}/recalculate')
def recalculate(id:int,db:Session=DB,user=PROC):
    req=request_for(db,id,user,True);state(req,'QUOTATIONS_RECEIVED','COMPARISON_READY')
    if not db.scalar(select(Quotation).where(Quotation.requisition_id==id)):raise HTTPException(409,'At least one complete quotation required')
    req.status='COMPARISON_READY';audit(db,user,'COMPARISON_GENERATED',req);return comparison(id,db,user)

@router.get('/requisitions/{id}/comparison')
def comparison(id:int,db:Session=DB,user=USER):
    req=request_for(db,id,user);data=detail(db,req)
    for q in data['quotations']:q['risk']=risk_for(db,q['vendor_id'])
    data['lowest_total']=min((float(q['grand_total']) for q in data['quotations']),default=None)
    return data

@router.post('/requisitions/{id}/send-for-approval')
def send_for_approval(id:int,data:SelectionIn,db:Session=DB,user=PROC):
    req=request_for(db,id,user,True);state(req,'COMPARISON_READY')
    q=db.scalar(select(Quotation).where(Quotation.requisition_id==id,Quotation.vendor_id==data.vendor_id))
    if not q:raise HTTPException(422,'Select a vendor with a complete quotation')
    if not fetch(db,Vendor,data.vendor_id).active:raise HTTPException(409,'Selected vendor is inactive')
    if q.valid_until and q.valid_until<date.today():raise HTTPException(409,'Selected quotation has expired')
    rules=list(db.scalars(select(ApprovalRule).where(ApprovalRule.active==True,ApprovalRule.min_amount<=q.grand_total).order_by(ApprovalRule.level)))
    rules=[x for x in rules if x.max_amount is None or q.grand_total<x.max_amount]
    if not rules or len({x.level for x in rules})!=len(rules):raise HTTPException(409,'Approval policy is missing or ambiguous')
    req.approval_plan=[{'level':x.level,'role':x.required_role,'name':x.name} for x in rules]
    req.preferred_vendor_id=data.vendor_id;req.status='PENDING_APPROVAL'
    audit(db,user,'PREFERRED_VENDOR_PROPOSED',req,details=data.model_dump());audit(db,user,'SENT_FOR_APPROVAL',req,details={'plan':req.approval_plan});return row(req)

@router.get('/approvals/inbox')
def inbox(db:Session=DB,user=Depends(roles('approver','finance_admin'))):
    results=[]
    for req in db.scalars(select(Requisition).where(Requisition.status=='PENDING_APPROVAL')):
        done=len(list(db.scalars(select(Approval).where(Approval.requisition_id==req.id))))
        if req.approval_plan[done]['role']==user.role:results.append(row(req))
    return results

@router.post('/requisitions/{id}/approval')
def approve(id:int,data:DecisionIn,db:Session=DB,user=Depends(roles('approver','finance_admin'))):
    req=request_for(db,id,user,True);state(req,'PENDING_APPROVAL')
    if user.id==req.requester_id:raise HTTPException(403,'You cannot approve your own requisition')
    previous=list(db.scalars(select(Approval).where(Approval.requisition_id==id)))
    if any(x.approver_id==user.id for x in previous):raise HTTPException(409,'A different person must approve the next level')
    step=req.approval_plan[len(previous)]
    if step['role']!=user.role:raise HTTPException(403,'This approval level requires '+step['role'])
    db.add(Approval(requisition_id=id,approver_id=user.id,approval_level=step['level'],decision=data.decision,comment=data.comment))
    if data.decision=='REJECTED':req.status='REJECTED'
    elif len(previous)+1==len(req.approval_plan):req.status='APPROVED'
    audit(db,user,'APPROVAL_'+data.decision,req,details={'level':step['level'],'comment':data.comment});db.flush();return detail(db,req)

@router.get('/vendors/{id}/risk')
def risk(id:int,db:Session=DB,user=USER): fetch(db,Vendor,id);return risk_for(db,id)

@router.get('/requisitions/{id}/audit')
def logs(id:int,db:Session=DB,user=USER):
    request_for(db,id,user)
    return [dict(row(x),actor=fetch(db,Profile,x.actor_user_id).name if x.actor_user_id else 'Seed') for x in db.scalars(select(AuditLog).where(AuditLog.requisition_id==id).order_by(AuditLog.id))]

@router.post('/requisitions/{id}/purchase-order',status_code=201)
def issue_po(id:int,db:Session=DB,user=PROC):
    req=request_for(db,id,user,True);state(req,'APPROVED')
    q=db.scalar(select(Quotation).where(Quotation.requisition_id==id,Quotation.vendor_id==req.preferred_vendor_id))
    if q.valid_until and q.valid_until<date.today():raise HTTPException(409,'Approved quotation expired; start a new requisition')
    if not fetch(db,Vendor,q.vendor_id).active:raise HTTPException(409,'Approved vendor is inactive')
    po=PurchaseOrder(requisition_id=id,vendor_id=q.vendor_id,po_number=f'PO-{date.today().year}-{uuid4().hex[:10].upper()}',total=q.grand_total,snapshot_json={'requisition':row(req),'items':detail(db,req)['items'],'quotation':quote_view(db,q)})
    db.add(po);req.status='PO_ISSUED';db.flush();audit(db,user,'PO_ISSUED',req,details={'po_number':po.po_number});return row(po)

@router.get('/purchase-orders/{id}')
def po_detail(id:int,db:Session=DB,user=USER):
    po=fetch(db,PurchaseOrder,id);req=request_for(db,po.requisition_id,user)
    result=row(po);result['requisition_status']=req.status
    result['deliveries']=[row(x) for x in db.scalars(select(Delivery).where(Delivery.purchase_order_id==id))]
    inv=db.scalar(select(Invoice).where(Invoice.purchase_order_id==id));result['invoice']=row(inv) if inv else None
    result['documents']=[{k:v for k,v in row(d).items() if k!='storage_key'} for d in db.scalars(select(Document).where(Document.invoice_id==inv.id))] if inv else []
    return result

@router.post('/purchase-orders/{id}/delivery',status_code=201)
def delivery(id:int,data:DeliveryIn,db:Session=DB,user=Depends(roles('procurement','finance_admin'))):
    po=fetch(db,PurchaseOrder,id);req=request_for(db,po.requisition_id,user,True);state(req,'PO_ISSUED')
    if data.delivered_at<po.issued_at.date():raise HTTPException(422,'Delivery predates purchase order')
    d=Delivery(purchase_order_id=id,**data.model_dump());db.add(d)
    if data.status=='DELIVERED':req.status='DELIVERED';po.status='DELIVERED'
    audit(db,user,'DELIVERY_RECORDED',req,details={'status':data.status});db.flush();return row(d)

@router.post('/purchase-orders/{id}/invoice',status_code=201)
def invoice(id:int,data:InvoiceIn,db:Session=DB,user=FIN):
    po=fetch(db,PurchaseOrder,id);req=request_for(db,po.requisition_id,user,True);state(req,'DELIVERED')
    if data.invoice_date<po.issued_at.date():raise HTTPException(422,'Invoice predates purchase order')
    flag,reason=invoice_mismatch(data.amount,po.total)
    inv=Invoice(purchase_order_id=id,**data.model_dump(),mismatch_flag=flag,mismatch_reason=reason,status='REVIEW_REQUIRED' if flag else 'ACCEPTED')
    db.add(inv);req.status='INVOICED';audit(db,user,'INVOICE_RECORDED',req,details={'mismatch':flag});db.flush();return row(inv)

@router.post('/purchase-orders/{id}/close')
def close(id:int,data:CommentIn,db:Session=DB,user=FIN):
    po=fetch(db,PurchaseOrder,id);req=request_for(db,po.requisition_id,user,True);state(req,'INVOICED')
    inv=db.scalar(select(Invoice).where(Invoice.purchase_order_id==id))
    inv.resolution_comment=data.comment;inv.status='ACCEPTED_WITH_REVIEW' if inv.mismatch_flag else 'ACCEPTED'
    req.status='CLOSED';po.status='CLOSED';audit(db,user,'WORKFLOW_CLOSED',req,details={'comment':data.comment,'mismatch_reviewed':inv.mismatch_flag});return row(req)

async def upload_document(db,user,req,file,quotation_id=None,invoice_id=None):
    query=select(Document).where(Document.quotation_id==quotation_id) if quotation_id else select(Document).where(Document.invoice_id==invoice_id)
    if db.scalar(query):raise HTTPException(409,'Document already attached; evidence cannot be overwritten')
    data=await file.read(settings.max_upload+1);key,ctype,sha=storage.save(data)
    doc=Document(requisition_id=req.id,quotation_id=quotation_id,invoice_id=invoice_id,storage_key=key,backend=settings.storage_backend,sha256=sha,original_name=(file.filename or 'document').replace('\\','/').split('/')[-1][:180],content_type=ctype,size_bytes=len(data))
    db.add(doc);db.flush();audit(db,user,'DOCUMENT_UPLOADED',req,details={'document_id':doc.id,'sha256':sha});return {k:v for k,v in row(doc).items() if k!='storage_key'}

@router.post('/quotations/{id}/file',status_code=201)
async def quote_file(id:int,file:UploadFile=File(...),db:Session=DB,user=PROC):
    q=fetch(db,Quotation,id);req=request_for(db,q.requisition_id,user,True);state(req,'QUOTATIONS_RECEIVED','COMPARISON_READY')
    return await upload_document(db,user,req,file,quotation_id=id)

@router.post('/invoices/{id}/file',status_code=201)
async def invoice_file(id:int,file:UploadFile=File(...),db:Session=DB,user=FIN):
    inv=fetch(db,Invoice,id);po=fetch(db,PurchaseOrder,inv.purchase_order_id);req=request_for(db,po.requisition_id,user,True);state(req,'INVOICED')
    return await upload_document(db,user,req,file,invoice_id=id)

@router.get('/documents/{id}')
def download(id:int,db:Session=DB,user=USER):
    doc=fetch(db,Document,id);request_for(db,doc.requisition_id,user)
    return Response(storage.read(doc),media_type=doc.content_type,headers={'Content-Disposition':f'attachment; filename="document-{id}"','X-Document-SHA256':doc.sha256,'X-Content-Type-Options':'nosniff'})

