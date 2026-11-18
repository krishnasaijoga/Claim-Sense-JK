import sqlite3
from app.db import get_prior_claims,get_policy


def get_policy_context(
        policy_number:str,
        reference_date:str
)->dict:
    try:
        rows=get_policy(policy_number=policy_number)
    except sqlite3.DatabaseError as exc:
        return {
            "status":"POLICY_LOOKUP_UNAVAILABLE",
            "policy_number":policy_number,
            "error":str(exc)
        }
    if rows is None:
        return {
            "status":"POLICY_NOT_FOUND",
            "policy_number":policy_number
        }
    try:
        count=get_prior_claims(policy_number=policy_number,reference_date=reference_date)
    except sqlite3.DatabaseError as exc:
        return {
            **dict(rows),
            "status":"PRIOR_CLAIMS_UNAVAILABLE",
            "prior_claims_count":None,
            "error":str(exc)
        }
    return {
            "status":"SUCCESS",
            **dict(rows),
            "prior_claims_count":count
        }