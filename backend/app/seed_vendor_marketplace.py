"""Idempotent demo marketplace seed for the vendor/RFQ workflow.

Creates a realistic established supplier network with historical performance.
It never deletes transactional data. Known legacy aliases are also given the
same baseline history so an older demo supplier is not shown as history-less.
"""
from datetime import date, timedelta
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.entities import Department, Vendor, VendorHistory, PriceHistory, ApprovalRule

DEPARTMENTS=[
    ('Information Technology','CC-IT'),
    ('Administration','CC-ADM'),
    ('Library','CC-LIB'),
]

# name, portal email, contact, history profile
VENDORS=[
    ('Vertex Equipment','vendor.vertex@example.com','Enterprise Sales · +91 90000 11001',dict(total_orders=36,completed_orders=35,late_deliveries=2,anomalous_lines=2,quotation_lines=54,disputed_orders=1,incomplete_orders=1,invoice_mismatches=1,invoiced_orders=34)),
    ('Northstar Technologies','vendor.northstar@example.com','Institutional Accounts · +91 90000 11002',dict(total_orders=28,completed_orders=24,late_deliveries=5,anomalous_lines=8,quotation_lines=44,disputed_orders=3,incomplete_orders=4,invoice_mismatches=2,invoiced_orders=23)),
    ('Bluebell Networks','vendor.bluebell@example.com','Education Desk · +91 90000 11003',dict(total_orders=31,completed_orders=22,late_deliveries=9,anomalous_lines=14,quotation_lines=48,disputed_orders=6,incomplete_orders=9,invoice_mismatches=5,invoiced_orders=21)),
    ('Cedar Office Systems','vendor.cedar@example.com','Corporate Sales · +91 90000 11004',dict(total_orders=42,completed_orders=40,late_deliveries=3,anomalous_lines=4,quotation_lines=60,disputed_orders=2,incomplete_orders=2,invoice_mismatches=1,invoiced_orders=39)),
    ('Harbor Business Supply','vendor.harbor@example.com','Institutional Supply · +91 90000 11005',dict(total_orders=25,completed_orders=23,late_deliveries=4,anomalous_lines=5,quotation_lines=36,disputed_orders=2,incomplete_orders=2,invoice_mismatches=2,invoiced_orders=22)),
    ('Metro Digital Works','vendor.metro@example.com','Solutions Desk · +91 90000 11006',dict(total_orders=33,completed_orders=27,late_deliveries=7,anomalous_lines=10,quotation_lines=46,disputed_orders=4,incomplete_orders=6,invoice_mismatches=3,invoiced_orders=26)),
    ('Summit Workspace','vendor.summit@example.com','Workspace Sales · +91 90000 11007',dict(total_orders=29,completed_orders=27,late_deliveries=3,anomalous_lines=5,quotation_lines=39,disputed_orders=2,incomplete_orders=2,invoice_mismatches=1,invoiced_orders=26)),
    ('Juniper Stationery','vendor.juniper@example.com','Institutional Desk · +91 90000 11008',dict(total_orders=48,completed_orders=46,late_deliveries=4,anomalous_lines=3,quotation_lines=65,disputed_orders=1,incomplete_orders=2,invoice_mismatches=2,invoiced_orders=45)),
    ('Pioneer Electronics','vendor.pioneer@example.com','Enterprise Accounts · +91 90000 11009',dict(total_orders=21,completed_orders=17,late_deliveries=6,anomalous_lines=8,quotation_lines=32,disputed_orders=4,incomplete_orders=4,invoice_mismatches=3,invoiced_orders=17)),
    ('New Leaf Supplies','vendor.newleaf@example.com','Sales Desk · +91 90000 11010',dict(total_orders=18,completed_orders=16,late_deliveries=2,anomalous_lines=3,quotation_lines=28,disputed_orders=1,incomplete_orders=2,invoice_mismatches=1,invoiced_orders=15)),
]

ALIASES={
    'northstar':'Northstar Technologies',
    'north star':'Northstar Technologies',
    'vertex':'Vertex Equipment',
    'bluebell':'Bluebell Networks',
}

CATALOG=[
    ('Business laptop','Computers',52000),
    ('Office monitor','Displays',14000),
    ('Laser printer','Printing',22000),
    ('Ergonomic chair','Furniture',6500),
    ('Network switch','Networking',8000),
    ('UPS 1kVA','Power',9000),
    ('Projector','AV',36000),
    ('External SSD','Storage',5500),
    ('Keyboard','Accessories',900),
    ('A4 paper box','Stationery',1500),
]


def apply_history(db,vendor,values):
    history=db.scalar(select(VendorHistory).where(VendorHistory.vendor_id==vendor.id))
    created=not bool(history)
    if not history:
        history=VendorHistory(vendor_id=vendor.id)
        db.add(history)
    for key,value in values.items():
        setattr(history,key,value)
    return created


def upsert(db):
    created={'departments':0,'vendors':0,'histories':0,'price_history':0,'approval_rules':0,'legacy_aliases_enriched':0}
    for name,cost_center in DEPARTMENTS:
        dep=db.scalar(select(Department).where(Department.name==name))
        if not dep:
            db.add(Department(name=name,cost_center=cost_center));created['departments']+=1
        else:
            dep.cost_center=cost_center
    db.flush()

    specs={name:(email,contact,history) for name,email,contact,history in VENDORS}
    for name,email,contact,history_values in VENDORS:
        vendor=db.scalar(select(Vendor).where(Vendor.name==name))
        if not vendor:
            vendor=Vendor(name=name,email=email,contact=contact,active=True)
            db.add(vendor);db.flush();created['vendors']+=1
        else:
            vendor.email=email;vendor.contact=contact;vendor.active=True
        if apply_history(db,vendor,history_values):created['histories']+=1

    # Repair common manually-created demo aliases without deleting or re-keying them.
    for vendor in list(db.scalars(select(Vendor))):
        canonical=ALIASES.get(vendor.name.strip().lower())
        if canonical and vendor.name!=canonical:
            _,_,history_values=specs[canonical]
            if apply_history(db,vendor,history_values):created['histories']+=1
            created['legacy_aliases_enriched']+=1

    source='marketplace-demo-v2'
    has_market_history=db.scalar(select(PriceHistory.id).where(PriceHistory.source==source).limit(1))
    if not has_market_history:
        for item_name,category,price in CATALOG:
            for i,factor in enumerate([.94,.97,.98,1,1,1.02,1.03,1.06]):
                db.add(PriceHistory(
                    item_name=item_name,category=category,unit='piece',unit_price=round(price*factor,2),
                    observed_at=date.today()-timedelta(days=180-i*15),source=source,
                ))
                created['price_history']+=1

    rules=[
        ('Purchase committee',0,None,'approver',1),
        ('Senior finance approval',100000,None,'finance_admin',2),
    ]
    for name,min_amount,max_amount,role,level in rules:
        rule=db.scalar(select(ApprovalRule).where(ApprovalRule.name==name,ApprovalRule.level==level))
        if not rule:
            db.add(ApprovalRule(name=name,min_amount=min_amount,max_amount=max_amount,required_role=role,level=level,active=True));created['approval_rules']+=1
        else:
            rule.min_amount=min_amount;rule.max_amount=max_amount;rule.required_role=role;rule.active=True
    db.flush()
    return created


if __name__=='__main__':
    with SessionLocal.begin() as db:
        result=upsert(db)
    print('Vendor marketplace seed applied:',result)
    print('Established vendor network:',', '.join(name for name,_,_,_ in VENDORS))
