"""Local, isolated API benchmark; does NOT invent a human manual baseline."""
import argparse,json,sys,time,statistics,platform
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'backend'))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base,get_db
from app.core.auth import current_user
from app.models.entities import Profile
from app.seed import seed
p=argparse.ArgumentParser();p.add_argument('--runs',type=int,default=100);p.add_argument('--manual-seconds',type=float);p.add_argument('--system-seconds',type=float);p.add_argument('--output',default=str(root/'docs/evidence/baseline-benchmark.json'));args=p.parse_args()
if args.runs<1:raise SystemExit('runs must be positive')
engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool);Base.metadata.create_all(engine);sessions=sessionmaker(engine,expire_on_commit=False)
with sessions.begin() as db:
    seed(db);u=Profile(supabase_user_id='benchmark-only',name='Benchmark procurement',email='benchmark@example.com',role='procurement');db.add(u);db.flush()
def db_override():
    with sessions() as db:yield db
app.dependency_overrides[get_db]=db_override;app.dependency_overrides[current_user]=lambda:u
try:
    with TestClient(app) as client:
        timings=[]
        for _ in range(args.runs):
            start=time.perf_counter();res=client.get('/api/v1/requisitions/3/comparison');timings.append((time.perf_counter()-start)*1000);assert res.status_code==200
        data=res.json();totals=[q['grand_total'] for q in data['quotations']];expected=[121540,127440,169920]
        assert totals==expected,(totals,expected)
        assert data['quotations'][2]['items'][0]['analysis']['anomaly_flag']
    report={'run_at_utc':datetime.now(timezone.utc).isoformat(),'environment':platform.platform(),'python':platform.python_version(),'scope':'isolated SQLite TestClient; fixture identity; no network or live Supabase','runs':args.runs,'median_ms':round(statistics.median(timings),3),'p95_ms':round(sorted(timings)[max(0,int(.95*len(timings))-1)],3),'max_ms':round(max(timings),3),'expected_totals':expected,'actual_totals':totals,'correct_cases':3,'total_cases':3,'manual_workflow_seconds':args.manual_seconds,'system_human_workflow_seconds':args.system_seconds,'cycle_time_reduction_percent':None}
    if args.manual_seconds is not None and args.system_seconds is not None:
        if args.manual_seconds<=0 or args.system_seconds<0:raise SystemExit('Invalid observed times')
        report['cycle_time_reduction_percent']=round((args.manual_seconds-args.system_seconds)/args.manual_seconds*100,2)
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:app.dependency_overrides.clear();engine.dispose()
