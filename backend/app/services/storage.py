import hashlib
from pathlib import Path
from uuid import uuid4
import httpx
from fastapi import HTTPException
from app.core.config import settings

def detect_type(data):
    if data.startswith(b'%PDF-'): return 'application/pdf','.pdf'
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'image/png','.png'
    if data.startswith(b'\xff\xd8\xff'): return 'image/jpeg','.jpg'
    raise HTTPException(422,'Only PDF, PNG or JPEG file signatures are accepted')
def save(data):
    if not data or len(data)>settings.max_upload: raise HTTPException(413,'Document is empty or exceeds upload limit')
    content_type,ext=detect_type(data); key=uuid4().hex+ext
    if settings.storage_backend=='local':
        folder=Path(settings.upload_dir);folder.mkdir(parents=True,exist_ok=True);(folder/key).write_bytes(data)
    elif settings.storage_backend=='supabase':
        try:
            response=httpx.post(settings.supabase_url+'/storage/v1/object/'+settings.bucket+'/'+key,headers={'Authorization':'Bearer '+settings.service_key,'apikey':settings.service_key,'Content-Type':content_type},content=data,timeout=30)
            response.raise_for_status()
        except httpx.HTTPError: raise HTTPException(503,'Document storage unavailable; retry later')
    else: raise HTTPException(503,'Unsupported storage configuration')
    return key,content_type,hashlib.sha256(data).hexdigest()
def read(doc):
    try:
        if doc.backend=='local': data=(Path(settings.upload_dir)/doc.storage_key).read_bytes()
        else:
            response=httpx.get(settings.supabase_url+'/storage/v1/object/authenticated/'+settings.bucket+'/'+doc.storage_key,headers={'Authorization':'Bearer '+settings.service_key,'apikey':settings.service_key},timeout=30);response.raise_for_status();data=response.content
    except (OSError,httpx.HTTPError): raise HTTPException(503,'Document storage unavailable')
    if hashlib.sha256(data).hexdigest()!=doc.sha256: raise HTTPException(409,'Document integrity check failed')
    return data
