from decimal import Decimal
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from app.models.entities import *

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

def detail(db,req):
    result=row(req)
    result['items']=[row(x) for x in db.scalars(select(RequisitionItem).where(RequisitionItem.requisition_id==req.id).order_by(RequisitionItem.id))]
    result['invitations']=[dict(row(x),vendor=row(fetch(db,Vendor,x.vendor_id))) for x in db.scalars(select(Invitation).where(Invitation.requisition_id==req.id))]
    result['quotations']=[quote_view(db,q) for q in db.scalars(select(Quotation).where(Quotation.requisition_id==req.id))]
    result['approvals']=[row(x) for x in db.scalars(select(Approval).where(Approval.requisition_id==req.id).order_by(Approval.approval_level))]
    po=db.scalar(select(PurchaseOrder).where(PurchaseOrder.requisition_id==req.id))
    result['purchase_order']=row(po) if po else None
    return result

