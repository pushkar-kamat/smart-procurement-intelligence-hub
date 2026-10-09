import os
from pathlib import Path
from dotenv import load_dotenv

config_path = Path(__file__).resolve()

# backend/.env if present
load_dotenv(config_path.parents[2] / '.env')

# Project-root .env when running locally
if len(config_path.parents) > 3:
    load_dotenv(config_path.parents[3] / '.env')
class Settings:
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./procurement.db')
    supabase_url = os.getenv('SUPABASE_URL', '').rstrip('/')
    anon_key = os.getenv('SUPABASE_ANON_KEY', '')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    audience = os.getenv('SUPABASE_JWT_AUDIENCE', 'authenticated')
    auth_provider = os.getenv('AUTH_PROVIDER', 'supabase').strip().lower()
    local_auth_secret = os.getenv('LOCAL_AUTH_SECRET', '')
    local_auth_token_minutes = int(os.getenv('LOCAL_AUTH_TOKEN_MINUTES', '480'))
    storage_backend = os.getenv('STORAGE_BACKEND', 'local')
    aws_region = os.getenv('AWS_REGION', 'ap-south-1')
    s3_bucket = os.getenv('S3_BUCKET', '')
    upload_dir = os.getenv('LOCAL_UPLOAD_DIR', './uploads')
    bucket = os.getenv('SUPABASE_STORAGE_BUCKET', 'procurement-documents')
    max_upload = int(os.getenv('MAX_UPLOAD_MB', '10')) * 1024 * 1024
    price_threshold = float(os.getenv('PRICE_ANOMALY_PERCENT_THRESHOLD', '25'))
    risk_low = float(os.getenv('RISK_LOW_MAX', '29.99'))
    risk_medium = float(os.getenv('RISK_MEDIUM_MAX', '59.99'))
    mismatch_threshold = float(os.getenv('INVOICE_MISMATCH_PERCENT_THRESHOLD', '5'))
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
settings = Settings()
