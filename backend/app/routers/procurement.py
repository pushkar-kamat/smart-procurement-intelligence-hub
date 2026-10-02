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

from app.services.intelligence import money, calculate_line

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

