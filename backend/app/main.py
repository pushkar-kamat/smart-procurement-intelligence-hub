import json, logging, time
from collections import Counter
from uuid import uuid4
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.database import get_db
from app.core.auth import roles
from app.core.config import settings
from app.routers.procurement import router
app=FastAPI(title='Smart Procurement Intelligence Hub',version='1.0.0',description='BCA-08 • human-controlled procurement with explainable decision support')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.frontend_url.split(',')],allow_credentials=False,allow_methods=['GET','POST','PUT','PATCH','OPTIONS'],allow_headers=['Authorization','Content-Type'])
logger=logging.getLogger('procurement');logging.basicConfig(level=logging.INFO,format='%(message)s')
counters=Counter()
@app.middleware('http')
async def observe(request:Request,call_next):
    started=time.perf_counter();request_id=uuid4().hex
    response=await call_next(request)
    counters['requests']+=1;counters['errors']+=int(response.status_code>=400)
    counters['failed_authorization']+=int(response.status_code in [401,403])
    counters['approval_actions']+=int(request.url.path.endswith('/approval') and response.status_code<300)
    counters['total_duration_ms']+=round((time.perf_counter()-started)*1000,2)
    logger.info(json.dumps({'request_id':request_id,'method':request.method,'path':request.url.path,'status':response.status_code,'duration_ms':round((time.perf_counter()-started)*1000,2)}))
    response.headers['X-Request-ID']=request_id;response.headers['X-Content-Type-Options']='nosniff'
    return response
@app.exception_handler(IntegrityError)
async def conflict(request,exc):return JSONResponse(status_code=409,content={'detail':'Duplicate or conflicting record; refresh and retry'})
@app.exception_handler(SQLAlchemyError)
async def database_failure(request,exc):
    logger.error(json.dumps({'event':'database_unavailable','path':request.url.path}))
    return JSONResponse(status_code=503,content={'detail':'Database unavailable; retry later'})
@app.exception_handler(Exception)
async def controlled_failure(request,exc):
    logger.error(json.dumps({'event':'unexpected_failure','path':request.url.path,'type':type(exc).__name__}))
    return JSONResponse(status_code=500,content={'detail':'Unexpected server error; contact administrator'})
@app.get('/health')
def health(db=Depends(get_db,scope="function")):
    db.execute(text('SELECT 1'));return {'status':'ok','database':'reachable','auth_configured':bool(settings.supabase_url),'storage':settings.storage_backend}
@app.get('/metrics')
def metrics(user=Depends(roles('finance_admin'))):return {'counters':dict(counters),'scope':'this process since startup'}
app.include_router(router)
