import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from services.db_service import fetch_one


result = fetch_one("SELECT 'Oracle 연결 성공' AS message FROM dual")
print(result)