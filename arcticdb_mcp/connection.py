import os
from functools import cache

from arcticdb import Arctic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_URI_EXAMPLES = """\
  Local:  lmdb:///path/to/your/database
  S3:     s3://s3.amazonaws.com:bucket?region=us-east-1&access=KEY&secret=SECRET
  Azure:  azure://AccountName=X;AccountKey=Y;Container=Z"""


@cache
def get_ac() -> Arctic:
    uri = os.getenv("ARCTICDB_URI")
    if not uri:
        raise RuntimeError(f"ARCTICDB_URI is not set. Examples:\n{_URI_EXAMPLES}")
    try:
        return Arctic(uri)
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to ArcticDB: {e}\nExamples:\n{_URI_EXAMPLES}"
        ) from e
