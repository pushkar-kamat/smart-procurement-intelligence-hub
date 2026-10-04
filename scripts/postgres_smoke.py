"""Run the actual API regression suite in isolated PostgreSQL schemas."""
import os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
url=os.environ.get('DATABASE_URL','')
if not url.startswith('postgresql'):raise SystemExit('Set DATABASE_URL to a disposable PostgreSQL test database. Requires CREATE SCHEMA.')
env={**os.environ,'TEST_DATABASE_URL':url}
raise SystemExit(subprocess.call([sys.executable,'-m','pytest','-q'],cwd=root/'backend',env=env))
