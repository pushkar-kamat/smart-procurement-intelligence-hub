from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, JSON, UniqueConstraint, CheckConstraint
from app.core.database import Base

def now(): return datetime.now(timezone.utc)
def fk(table, **kw): return Column(Integer, ForeignKey(table+'.id'), **kw)
def money(**kw): return Column(Numeric(16,2), **kw)
class Department(Base):
    __tablename__='departments'
    id=Column(Integer,primary_key=True)
    name=Column(String(120),unique=True,nullable=False)
    cost_center=Column(String(40),nullable=False)
class Profile(Base):
    __tablename__='profiles'
    id=Column(Integer,primary_key=True)
    supabase_user_id=Column(String(64),unique=True,nullable=False)
    email=Column(String(254),unique=True,nullable=False)
    name=Column(String(120),nullable=False)
    role=Column(String(30),nullable=False,default='requester')
    department_id=fk('departments',nullable=True)
    active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime(timezone=True),default=now,nullable=False)
    __table_args__=(CheckConstraint("role IN ('requester','procurement','approver','finance_admin','vendor')"),)
class Vendor(Base):
    __tablename__='vendors'
    id=Column(Integer,primary_key=True)
    name=Column(String(120),unique=True,nullable=False)
    email=Column(String(254),nullable=False)
    contact=Column(String(80),default='')
    active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime(timezone=True),default=now)
class Requisition(Base):
    __tablename__='requisitions'
    id=Column(Integer,primary_key=True)
    requester_id=fk('profiles',nullable=False,index=True)
    department_id=fk('departments',nullable=False)
    title=Column(String(180),nullable=False)
    justification=Column(String(2000),nullable=False)
    status=Column(String(32),nullable=False,default='DRAFT',index=True)
    estimated_total=money(nullable=False)
    preferred_vendor_id=fk('vendors',nullable=True)
    selection_reason=Column(String(2000),nullable=True)
    approval_plan=Column(JSON,nullable=True)
    created_at=Column(DateTime(timezone=True),default=now)
    submitted_at=Column(DateTime(timezone=True))
    __table_args__=(CheckConstraint("status IN ('DRAFT','SUBMITTED','SOURCING','QUOTATIONS_RECEIVED','COMPARISON_READY','PENDING_APPROVAL','APPROVED','REJECTED','PO_ISSUED','DELIVERED','INVOICED','CLOSED','CANCELLED')"),)
class RequisitionItem(Base):
    __tablename__='requisition_items'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,index=True)
    item_name=Column(String(120),nullable=False)
    category=Column(String(80),nullable=False)
    description=Column(String(500),default='')
    quantity=Column(Numeric(12,3),nullable=False)
    unit=Column(String(30),nullable=False)
    estimated_unit_price=money(nullable=False)
    estimated_line_total=money(nullable=False)
    __table_args__=(CheckConstraint('quantity > 0'),CheckConstraint('estimated_unit_price > 0'))
class Invitation(Base):
    __tablename__='vendor_invitations'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,index=True)
    vendor_id=fk('vendors',nullable=False)
    invited_at=Column(DateTime(timezone=True),default=now)
    status=Column(String(30),default='INVITED')
    response_at=Column(DateTime(timezone=True))
    __table_args__=(UniqueConstraint('requisition_id','vendor_id'),)
class Quotation(Base):
    __tablename__='quotations'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,index=True)
    vendor_id=fk('vendors',nullable=False,index=True)
    quotation_number=Column(String(80),nullable=False)
    quotation_date=Column(Date,nullable=False)
    valid_until=Column(Date,nullable=True)
    delivery_days=Column(Integer,nullable=False)
    delivery_terms=Column(String(500),default='')
    subtotal=money(nullable=False)
    tax_total=money(nullable=False)
    discount_total=money(nullable=False)
    grand_total=money(nullable=False)
    created_at=Column(DateTime(timezone=True),default=now)
    __table_args__=(UniqueConstraint('requisition_id','vendor_id'),)
class QuotationItem(Base):
    __tablename__='quotation_items'
    id=Column(Integer,primary_key=True)
    quotation_id=fk('quotations',nullable=False,index=True)
    requisition_item_id=fk('requisition_items',nullable=False)
    unit_price=money(nullable=False)
    quantity=Column(Numeric(12,3),nullable=False)
    tax=money(nullable=False)
    discount=money(nullable=False)
    line_total=money(nullable=False)
    analysis=Column(JSON,nullable=False)
    __table_args__=(UniqueConstraint('quotation_id','requisition_item_id'),CheckConstraint('unit_price > 0'),CheckConstraint('quantity > 0'))
class PriceHistory(Base):
    __tablename__='price_history'
    id=Column(Integer,primary_key=True)
    item_name=Column(String(120),nullable=False,index=True)
    category=Column(String(80),nullable=False,index=True)
    unit=Column(String(30),nullable=False)
    unit_price=money(nullable=False)
    observed_at=Column(Date,nullable=False)
    source=Column(String(120),nullable=False)
class VendorHistory(Base):
    __tablename__='vendor_history'
    id=Column(Integer,primary_key=True)
    vendor_id=fk('vendors',nullable=False,unique=True)
    total_orders=Column(Integer,default=0,nullable=False)
    completed_orders=Column(Integer,default=0,nullable=False)
    late_deliveries=Column(Integer,default=0,nullable=False)
    anomalous_lines=Column(Integer,default=0,nullable=False)
    quotation_lines=Column(Integer,default=0,nullable=False)
    disputed_orders=Column(Integer,default=0,nullable=False)
    incomplete_orders=Column(Integer,default=0,nullable=False)
    invoice_mismatches=Column(Integer,default=0,nullable=False)
    invoiced_orders=Column(Integer,default=0,nullable=False)
class ApprovalRule(Base):
    __tablename__='approval_rules'
    id=Column(Integer,primary_key=True)
    name=Column(String(100),nullable=False)
    min_amount=money(nullable=False)
    max_amount=money(nullable=True)
    required_role=Column(String(30),nullable=False)
    level=Column(Integer,nullable=False)
    active=Column(Boolean,default=True,nullable=False)
class Approval(Base):
    __tablename__='approvals'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,index=True)
    approver_id=fk('profiles',nullable=False)
    approval_level=Column(Integer,nullable=False)
    decision=Column(String(20),nullable=False)
    comment=Column(String(2000),nullable=False)
    decided_at=Column(DateTime(timezone=True),default=now)
    __table_args__=(UniqueConstraint('requisition_id','approval_level'),UniqueConstraint('requisition_id','approver_id'))
class PurchaseOrder(Base):
    __tablename__='purchase_orders'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,unique=True)
    vendor_id=fk('vendors',nullable=False)
    po_number=Column(String(60),nullable=False,unique=True)
    total=money(nullable=False)
    issued_at=Column(DateTime(timezone=True),default=now)
    status=Column(String(30),default='ISSUED')
    snapshot_json=Column(JSON,nullable=False)
class Delivery(Base):
    __tablename__='deliveries'
    id=Column(Integer,primary_key=True)
    purchase_order_id=fk('purchase_orders',nullable=False,index=True)
    status=Column(String(30),nullable=False)
    delivered_at=Column(Date,nullable=False)
    expected_completion_at=Column(Date,nullable=True)
    notes=Column(String(2000),nullable=False)
class Invoice(Base):
    __tablename__='invoices'
    id=Column(Integer,primary_key=True)
    purchase_order_id=fk('purchase_orders',nullable=False,unique=True)
    invoice_number=Column(String(80),nullable=False)
    invoice_date=Column(Date,nullable=False)
    amount=money(nullable=False)
    status=Column(String(30),nullable=False)
    mismatch_flag=Column(Boolean,nullable=False)
    mismatch_reason=Column(String(500),nullable=False)
    resolution_comment=Column(String(2000),nullable=True)
class Document(Base):
    __tablename__='documents'
    id=Column(Integer,primary_key=True)
    requisition_id=fk('requisitions',nullable=False,index=True)
    quotation_id=fk('quotations',nullable=True,unique=True)
    invoice_id=fk('invoices',nullable=True,unique=True)
    storage_key=Column(String(200),nullable=False)
    backend=Column(String(20),nullable=False)
    sha256=Column(String(64),nullable=False)
    original_name=Column(String(180),nullable=False)
    content_type=Column(String(60),nullable=False)
    size_bytes=Column(Integer,nullable=False)
    created_at=Column(DateTime(timezone=True),default=now)
    __table_args__=(CheckConstraint('(quotation_id IS NULL) <> (invoice_id IS NULL)'),)
class AuditLog(Base):
    __tablename__='audit_logs'
    id=Column(Integer,primary_key=True)
    actor_user_id=fk('profiles',nullable=True)
    requisition_id=fk('requisitions',nullable=True,index=True)
    action=Column(String(80),nullable=False)
    entity_type=Column(String(60),nullable=False)
    entity_id=Column(Integer,nullable=False)
    timestamp=Column(DateTime(timezone=True),default=now,nullable=False)
    details=Column(JSON,nullable=False)
