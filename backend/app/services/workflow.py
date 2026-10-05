from datetime import date
from decimal import Decimal
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from app.models.entities import *
from app.services.intelligence import vendor_risk

def row(obj): return jsonable_encoder({c.name:getattr(obj,c.name) for c in obj.__table__.columns},custom_encoder={Decimal:float})
def fetch(db,cls,id):
    value=db.get(cls,id)
    if value is None: raise HTTPException(404,f'{cls.__name__} not found')
    return value

def request_for(db,id,user,lock=False):
    query=select(Requisition).where(Requisition.id==id)
    if lock: query=query.with_for_update()
    req=db.scalar(query)
    if req is None: raise HTTPException(404,'Requisition not found')
    if user.role=='requester' and req.requester_id!=user.id: raise HTTPException(403,'This requisition belongs to another requester')
    return req

def state(req,*allowed):
    if req.status not in allowed: raise HTTPException(409,f'Action unavailable in {req.status}; expected '+', '.join(allowed))

def audit(db,user,action,req=None,entity=None,details=None):
    entity=entity or req
    db.add(AuditLog(actor_user_id=user.id if user else None,requisition_id=req.id if req else None,action=action,entity_type=entity.__tablename__,entity_id=entity.id,details=details or {}))

def quote_view(db,q):
    result=row(q);result['vendor']=row(fetch(db,Vendor,q.vendor_id))
    result['items']=[row(i) for i in db.scalars(select(QuotationItem).where(QuotationItem.quotation_id==q.id).order_by(QuotationItem.id))]
    result['documents']=[{k:v for k,v in row(d).items() if k!='storage_key'} for d in db.scalars(select(Document).where(Document.quotation_id==q.id))]
    return result

def risk_for(db,vendor_id):
    history=db.scalar(select(VendorHistory).where(VendorHistory.vendor_id==vendor_id))
    facts=row(history) if history else {}
    # Synthetic baseline facts plus committed workflow observations, without counting issued orders as overdue.
    qs=list(db.scalars(select(Quotation).where(Quotation.vendor_id==vendor_id)))
    lines=list(db.scalars(select(QuotationItem).where(QuotationItem.quotation_id.in_([q.id for q in qs])))) if qs else []
    facts['quotation_lines']=facts.get('quotation_lines',0)+len(lines)
    facts['anomalous_lines']=facts.get('anomalous_lines',0)+sum(i.analysis['anomaly_flag'] for i in lines)
    pos=list(db.scalars(select(PurchaseOrder).where(PurchaseOrder.vendor_id==vendor_id)))
    for po in pos:
        deliveries=list(db.scalars(select(Delivery).where(Delivery.purchase_order_id==po.id)))
        completed=next((d for d in deliveries if d.status=='DELIVERED'),None)
        age=(date.today()-po.issued_at.date()).days
        overdue=age>po.snapshot_json['quotation']['delivery_days']
        if completed or overdue:
            facts['total_orders']=facts.get('total_orders',0)+1
            facts['incomplete_orders']=facts.get('incomplete_orders',0)+int(not completed)
        if completed:
            facts['completed_orders']=facts.get('completed_orders',0)+1
            late=(completed.delivered_at-po.issued_at.date()).days>po.snapshot_json['quotation']['delivery_days']
            facts['late_deliveries']=facts.get('late_deliveries',0)+int(late)
        inv=db.scalar(select(Invoice).where(Invoice.purchase_order_id==po.id))
        if inv:
            facts['invoiced_orders']=facts.get('invoiced_orders',0)+1
            facts['invoice_mismatches']=facts.get('invoice_mismatches',0)+int(inv.mismatch_flag)
    return vendor_risk(facts)

def detail(db,req):
    result=row(req)
    result['items']=[row(x) for x in db.scalars(select(RequisitionItem).where(RequisitionItem.requisition_id==req.id).order_by(RequisitionItem.id))]
    result['invitations']=[dict(row(x),vendor=row(fetch(db,Vendor,x.vendor_id))) for x in db.scalars(select(Invitation).where(Invitation.requisition_id==req.id))]
    result['quotations']=[quote_view(db,q) for q in db.scalars(select(Quotation).where(Quotation.requisition_id==req.id))]
    result['approvals']=[row(x) for x in db.scalars(select(Approval).where(Approval.requisition_id==req.id).order_by(Approval.approval_level))]
    if req.preferred_vendor_id:
        vendor=fetch(db,Vendor,req.preferred_vendor_id)
        result['preferred_vendor']=row(vendor)
        selected=db.scalar(select(Quotation).where(Quotation.requisition_id==req.id,Quotation.vendor_id==req.preferred_vendor_id))
        result['selected_quotation']=quote_view(db,selected) if selected else None
        result['preferred_vendor_risk']=risk_for(db,req.preferred_vendor_id)
    else:
        result['preferred_vendor']=None
        result['selected_quotation']=None
        result['preferred_vendor_risk']=None
    po=db.scalar(select(PurchaseOrder).where(PurchaseOrder.requisition_id==req.id))
    result['purchase_order']=row(po) if po else None
    return result
