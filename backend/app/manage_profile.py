"""Operator-only CLI for initial admin bootstrap; never an unauthenticated HTTP route."""
import argparse
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.entities import Profile,AuditLog
p=argparse.ArgumentParser();p.add_argument('email');p.add_argument('role',choices=['requester','procurement','approver','finance_admin']);args=p.parse_args()
with SessionLocal.begin() as db:
    user=db.scalar(select(Profile).where(Profile.email==args.email))
    if not user:raise SystemExit('User must sign in once first, then rerun.')
    old=user.role;user.role=args.role
    db.add(AuditLog(action='OPERATOR_ROLE_CHANGED',entity_type='profiles',entity_id=user.id,details={'previous_role':old,'role':args.role,'source':'operator CLI'}))
    print('Role updated for',args.email)
