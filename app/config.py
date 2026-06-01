import json
import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent

def get_secret(
    key:str,
    default_value:Optional[str]=None,
    json_path:str= str(BASE_DIR/"secrets.json")
):
    value= os.getenv(key)

    if value:
        return value
    try:
        with open(json_path,encoding="utf-8") as f:
            secrets=json.load(f)
        return secrets[key]

    except FileNotFoundError:
        pass
    except KeyError:
        pass

    if default_value is not None:
        return default_value

    raise EnvironmentError(f"Set the {key} environment variable")


MONGODB_DB_NAME = get_secret("MONGODB_DB_NAME")
MONGODB_URL = get_secret("MONGODB_URI")
NAVER_API_SECRET = get_secret("NAVER_API_SECRET")
NAVER_API_ID = get_secret("NAVER_API_ID")
