import pytest
import os
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy import create_engine,event,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base,get_db
from app.core.auth import current_user
from app.models.entities import Profile
from app.seed import seed

@pytest.fixture
def env(tmp_path,monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings,'upload_dir',str(tmp_path/'uploads'))
    test_url=os.getenv('TEST_DATABASE_URL')
    schema=None
    if test_url:
        assert test_url.startswith('postgresql'), 'TEST_DATABASE_URL must be PostgreSQL'
        engine=create_engine(test_url)
        schema='test_'+uuid4().hex
        with engine.begin() as conn:conn.execute(text('CREATE SCHEMA '+schema))
        engine=engine.execution_options(schema_translate_map={None:schema})
    else:
        engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
        @event.listens_for(engine,'connect')
        def fk(conn,_):conn.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    sessions=sessionmaker(engine,expire_on_commit=False)
    with sessions.begin() as db:
        seed(db)
        for name,role in [('procurement','procurement'),('approver','approver'),('finance','finance_admin'),('other','requester')]:
            db.add(Profile(supabase_user_id=name,email=name+'@example.com',name=name,role=role))
    def override():
        with sessions() as db:
            try:yield db;db.commit()
            except Exception:db.rollback();raise
    app.dependency_overrides[get_db]=override
    def login(role):
        with sessions() as db:
            email={'requester':'requester','finance_admin':'finance'}.get(role,role)+'@example.com'
            user=db.scalar(select(Profile).where(Profile.email==email))
        app.dependency_overrides[current_user]=lambda:user
        return user
    with TestClient(app,raise_server_exceptions=False) as client:yield client,login,sessions
    app.dependency_overrides.clear()
    if schema:
        with engine.begin() as conn:conn.execute(text('DROP SCHEMA '+schema+' CASCADE'))
    engine.dispose()
