import sqlite3
import time

from app import config
from contextlib import closing
from datetime import datetime
from dateutil.relativedelta import relativedelta


FETCH_POLICY_QUERY="""
SELECT * FROM policies WHERE policy_number = (?)
"""


def connect() -> sqlite3.Connection:
    """Open the database; rows behave like dicts (row['policy_number'])."""
    conn = sqlite3.connect(config.DB_PATH,timeout=0.5)
    conn.row_factory = sqlite3.Row
    return conn


def get_policy(policy_number:str,max_retries:int=3,base_delay:float=0.5)->dict|None:
    last_error=None
    if max_retries<1:
        raise ValueError("max_retries must be >=1")
    if base_delay<0.0:
        raise ValueError("base_delay must be >=0")
    for attempt in range(1,max_retries+1):
        try:
            with closing(connect()) as conn:
                row=conn.execute(
                    FETCH_POLICY_QUERY,(policy_number.strip(),)
                ).fetchone()
            return dict(row) if row else None
        except sqlite3.OperationalError as e:
            if getattr(e, "sqlite_errorcode", None) not in (
                sqlite3.SQLITE_BUSY,
                sqlite3.SQLITE_LOCKED
            ):
                raise

            last_error = e

            if attempt < max_retries:
                time.sleep(base_delay * (2 ** (attempt - 1)))
        except sqlite3.DatabaseError as e:
            raise
    print(f"Database operation failed after {max_retries} attempts")
    if last_error is not None:
        raise last_error
    

def get_prior_claims(policy_number:str, reference_date:str, max_retries:int=3,base_delay:float=0.5)->int: # type: ignore
    last_error=None
    if max_retries<1:
        raise ValueError("max_retries must be >=1")
    if base_delay<0.0:
        raise ValueError("base_delay must be >=0")
    end_date=datetime.strptime(reference_date,"%Y-%m-%d").date()
    start_date=end_date-relativedelta(months=12)
    PRIOR_CLAIMS_QUERY="""
    SELECT COUNT(*) FROM prior_claims WHERE policy_number = (?) AND claim_date>=(?) AND claim_date<=(?)
    """
    for attempt in range(1,max_retries+1):
        try:
            with closing(connect()) as conn:
                count=conn.execute(
                    PRIOR_CLAIMS_QUERY,(policy_number.strip(),start_date.isoformat(),end_date.isoformat())
                ).fetchone()
            return count[0]
        except sqlite3.OperationalError as e:
            if getattr(e, "sqlite_errorcode", None) not in (
                sqlite3.SQLITE_BUSY,
                sqlite3.SQLITE_LOCKED
            ):
                raise

            last_error = e

            if attempt < max_retries:
                time.sleep(base_delay * (2 ** (attempt - 1)))
    print(f"Database operation failed after {max_retries} attempts")
    if last_error is not None:
        raise last_error