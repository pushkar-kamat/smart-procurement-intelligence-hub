"""Explicit optional admin operation: creates staff plus vendor demo identities."""
import os
import httpx
from sqlalchemy import select
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Profile

ACCOUNTS=[
    ('requester@example.com','requester','Demo Requester'),
    ('procurement@example.com','procurement','Procurement Officer'),
    ('approver@example.com','approver','Purchase Approver'),
    ('finance@example.com','finance_admin','Finance Administrator'),
    ('vendor.vertex@example.com','vendor','Vertex Equipment'),
    ('vendor.northstar@example.com','vendor','Northstar Technologies'),
    ('vendor.bluebell@example.com','vendor','Bluebell Networks'),
    ('vendor.cedar@example.com','vendor','Cedar Office Systems'),
    ('vendor.harbor@example.com','vendor','Harbor Business Supply'),
    ('vendor.metro@example.com','vendor','Metro Digital Works'),
    ('vendor.summit@example.com','vendor','Summit Workspace'),
    ('vendor.juniper@example.com','vendor','Juniper Stationery'),
    ('vendor.pioneer@example.com','vendor','Pioneer Electronics'),
    ('vendor.newleaf@example.com','vendor','New Leaf Supplies'),
]

def main():
    password=os.getenv('DEMO_PASSWORD','')
    if len(password)<12 or not settings.service_key or not settings.supabase_url:raise SystemExit('Set DEMO_PASSWORD (12+ chars), SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY locally.')
    headers={'apikey':settings.service_key,'Authorization':'Bearer '+settings.service_key}
    with httpx.Client(base_url=settings.supabase_url+'/auth/v1',headers=headers,timeout=30) as client, SessionLocal.begin() as db:
        identities={};page=1
        while True:
            response=client.get('/admin/users',params={'page':page,'per_page':100});response.raise_for_status()
            users=response.json().get('users',[]);identities.update({u['email']:u for u in users if u.get('email')})
            if len(users)<100:break
            page+=1
        for email,role,name in ACCOUNTS:
            identity=identities.get(email)
            if not identity:
                response=client.post('/admin/users',json={'email':email,'password':password,'email_confirm':True});response.raise_for_status();identity=response.json()
            p=db.scalar(select(Profile).where(Profile.email==email))
            if not p:p=Profile(email=email,name=name);db.add(p)
            p.supabase_user_id=identity['id'];p.role=role;p.name=name;p.active=True
            print(email,role,'linked (existing passwords unchanged)')
if __name__=='__main__':main()
