import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


OPENAI_MODEL=os.getenv("OPENAI_MODEL","gpt-4.1-mini")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL","text-embedding-3-small")

# Price per 1 million tokens in USD: (input, output). Check https://openai.com/api/pricing before quoting costs.
PRICES_USD_PER_1M = {
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-5-mini": (0.25, 2.00),
    "text-embedding-3-small": (0.02, 0.0),
}
USD_TO_INR = float(os.getenv("USD_TO_INR", "88"))  # update to today's exchange rate

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "claims.db"                  # business data: policies, claims, audit log
CHECKPOINT_DB_PATH = DATA_DIR / "checkpoints.db"  # LangGraph state, so a paused claim can resume later
SAMPLE_CLAIMS_DIR = DATA_DIR / "sample_claims"    # 20 ready-made claims (PDFs) for demos and evals
UPLOADS_DIR = DATA_DIR / "uploads"                # claims submitted through the API / portal
POLICY_WORDING_PATH = DATA_DIR / "policy_wording.md"
POLICY_INDEX_PATH = DATA_DIR / "policy_index.json"  # cached embeddings of policy clauses
EVAL_LABELS_PATH = DATA_DIR / "eval_labels.csv"

# Business rules
AUTO_APPROVE_LIMIT_INR = 50_000      # above this, a human must approve even a clean claim
FRAUD_SIU_THRESHOLD = 50             # fraud score >= 50 -> Special Investigation Unit
FRAUD_REVIEW_THRESHOLD = 25          # fraud score 25-49 -> claims adjuster review
TOTAL_LOSS_RATIO = 0.75              # repair cost > 75% of IDV -> constructive total loss
INTIMATION_DAYS_LIMIT = 7            # claim should be reported within 7 days of the accident
EARLY_CLAIM_DAYS = 30                # accident within 30 days of policy start is a fraud signal
ESTIMATE_INFLATION_RATIO = 1.40      # garage estimate > 140% of surveyor assessment is a fraud signal
RETRIEVAL_TOP_K = 6                  # how many policy clauses to retrieve for the coverage check