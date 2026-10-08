"""Idempotent synthetic demo data. Run only after Alembic upgrade head."""
from datetime import date, timedelta
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.entities import *
from app.services.intelligence import analyze_price
CATALOG=[('Business laptop','Computers',52000),('Office monitor','Displays',14000),('Laser printer','Printing',22000),('Ergonomic chair','Furniture',6500),('Network switch','Networking',8000),('UPS 1kVA','Power',9000),('Projector','AV',36000),('External SSD','Storage',5500),('Keyboard','Accessories',900),('A4 paper box','Stationery',1500)]
NAMES=['Cedar Office Systems','Northstar Technologies','Harbor Business Supply','Metro Digital Works','Summit Workspace','Bluebell Networks','Vertex Equipment','Juniper Stationery','Pioneer Electronics','New Leaf Supplies']
def seed(db):
    if db.scalar(select(Vendor).limit(1)):return False
    deps=[Department(name=n,cost_center=c) for n,c in [('Information Technology','CC-IT'),('Administration','CC-ADM'),('Library','CC-LIB')]]
    db.add_all(deps);db.flush()
    profile=Profile(supabase_user_id='synthetic-requester-unlinked',email='requester@procure.com',name='Demo Requester',role='requester',department_id=deps[0].id)
    db.add(profile);db.flush()
    for idx,name in enumerate(NAMES):
        v=Vendor(name=name,email=f'vendor{idx+1}@procure.com',contact=f'Synthetic contact {idx+1}');db.add(v);db.flush()
        rate=[0.05,0.4,0.8][idx%3]
        if idx==9:db.add(VendorHistory(vendor_id=v.id))
        else:db.add(VendorHistory(vendor_id=v.id,total_orders=100,completed_orders=100-int(100*rate),late_deliveries=int((100-int(100*rate))*rate),anomalous_lines=int(40*rate),quotation_lines=40,disputed_orders=int(100*rate),incomplete_orders=int(100*rate),invoice_mismatches=int(20*rate),invoiced_orders=20))
    for name,category,price in CATALOG:
        for i,factor in enumerate([.94,.97,.98,1,1,1.02,1.03,1.06]):
            db.add(PriceHistory(item_name=name,category=category,unit='piece',unit_price=round(price*factor,2),observed_at=date.today()-timedelta(days=180-i*15),source='synthetic-v1'))
    db.add_all([ApprovalRule(name='Purchase committee',min_amount=0,max_amount=None,required_role='approver',level=1),ApprovalRule(name='Senior finance approval',min_amount=200000,max_amount=None,required_role='finance_admin',level=2)])
    for idx,(title,status) in enumerate([('Library workstation refresh','DRAFT'),('Administration display replacement','SUBMITTED'),('IT laptop procurement comparison','COMPARISON_READY')]):
        req=Requisition(requester_id=profile.id,department_id=deps[0].id,title=title,justification='Synthetic demonstration purchase for teaching and evaluation.',status=status,estimated_total=104000,submitted_at=now() if idx else None);db.add(req);db.flush()
        item=RequisitionItem(requisition_id=req.id,item_name='Business laptop',category='Computers',description='16 GB RAM, 512 GB SSD; equivalent specification for all vendors',quantity=2,unit='piece',estimated_unit_price=52000,estimated_line_total=104000);db.add(item);db.flush()
        db.add(AuditLog(actor_user_id=profile.id,requisition_id=req.id,action='SYNTHETIC_SCENARIO_SEEDED',entity_type='requisitions',entity_id=req.id,details={'provenance':'synthetic-v1','initial_state':status}))
        if idx==2:
            for vid,price in [(1,51500),(2,54000),(3,72000)]:
                db.add(Invitation(requisition_id=req.id,vendor_id=vid,status='RESPONDED',response_at=now()))
                q=Quotation(requisition_id=req.id,vendor_id=vid,quotation_number=f'DEMO-Q-{vid}',quotation_date=date.today(),valid_until=date.today()+timedelta(days=90),delivery_days=7+vid*3,delivery_terms='Delivery to campus, warranty 12 months',subtotal=price*2,tax_total=price*2*.18,discount_total=0,grand_total=price*2*1.18);db.add(q);db.flush()
                db.add(QuotationItem(quotation_id=q.id,requisition_item_id=item.id,unit_price=price,quantity=2,tax=price*2*.18,discount=0,line_total=price*2*1.18,analysis=analyze_price(price,[52000*f for f in [.94,.97,.98,1,1,1.02,1.03,1.06]])))
    db.flush();return True
if __name__=='__main__':
    with SessionLocal.begin() as db: print('Synthetic data created.' if seed(db) else 'Seed already present; no data changed.')
