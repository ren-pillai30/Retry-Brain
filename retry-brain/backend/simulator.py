import os
import time
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from decision_engine import evaluate_failure

# Automatically resolve paths relative to the project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DEFAULT_INPUT = DATA_DIR / "failed_payments_batch.csv"
DEFAULT_OUTPUT = DATA_DIR / "audit_trail.csv"

def run_simulation(
    input_csv=DEFAULT_INPUT,
    output_csv=DEFAULT_OUTPUT,
    limit=None,
    delay_seconds=2.0
):
    """
    Runs the AI recovery decision engine and naive baseline against failed payment records.
    """
    input_path = Path(input_csv)
    output_path = Path(output_csv)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find input file at: {input_path}\n"
            "Please run 'python data/generate_data.py' first to generate the synthetic batch."
        )
        
    print(f"Loading batch from {input_path}...")
    df = pd.read_csv(input_path)
    
    if limit:
        df = df.head(limit)
        print(f"Testing on first {limit} records...")

    audit_records = []
    
    print("Processing transactions through AI Agent & Naive Baseline...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        txn_data = {
            "transaction_id": str(row["transaction_id"]),
            "amount": float(row["amount"]),
            "failure_code": str(row["failure_code"]),
            "failure_reason_raw": str(row["failure_reason_raw"]),
            "payment_method": str(row["payment_method"])
        }
        
        would_succeed = bool(row["would_succeed_on_retry"])
        amount = float(row["amount"])

        # 1. NAIVE BASELINE (Blind retry up to 3 times for ALL failures)
        naive_max_attempts = 3
        if would_succeed:
            naive_attempts_used = 1
            naive_recovered = amount
        else:
            naive_attempts_used = naive_max_attempts
            naive_recovered = 0.0

        # 2. AI AGENT SIMULATION (Root-cause aware decision making)
        decision = evaluate_failure(txn_data)
        action = decision.get("recommended_action", "ABORT")
        max_allowed = int(decision.get("max_attempts_allowed", 0))

        ai_attempts_used = 0
        ai_recovered = 0.0

        if action in ["IMMEDIATE_RETRY", "DELAYED_RETRY_NOTIFY"]:
            if would_succeed:
                ai_attempts_used = 1
                ai_recovered = amount
            else:
                ai_attempts_used = max(1, max_allowed)
        else:
            # Correctly stopped on non-retryable errors (e.g., Expired Card, Do Not Honor)
            ai_attempts_used = 0
            ai_recovered = 0.0

        # 3. RECORD AUDIT ENTRY
        audit_records.append({
            "transaction_id": row["transaction_id"],
            "amount": amount,
            "failure_code": row["failure_code"],
            "ground_truth_succeed": would_succeed,
            
            # AI Decision Outputs
            "ai_root_cause": decision.get("root_cause_category", "Unknown"),
            "ai_action": action,
            "ai_reasoning": decision.get("reasoning", "N/A"),
            "ai_retry_delay_hours": decision.get("retry_delay_hours", 0),
            "ai_attempts_used": ai_attempts_used,
            "ai_recovered_amount": ai_recovered,
            
            # Naive Baseline Outputs
            "naive_attempts_used": naive_attempts_used,
            "naive_recovered_amount": naive_recovered
        })
        
        # Free-tier rate limit protection
        time.sleep(delay_seconds)

    # Save complete audit trail
    audit_df = pd.DataFrame(audit_records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(output_path, index=False)
    print(f"\nSimulation completed successfully! Audit trail exported to: {output_path}")

    # Summary Statistics Terminal Output
    total_at_risk = audit_df["amount"].sum()
    ai_recovered_total = audit_df["ai_recovered_amount"].sum()
    naive_recovered_total = audit_df["naive_recovered_amount"].sum()
    
    ai_retries = audit_df["ai_attempts_used"].sum()
    naive_retries = audit_df["naive_attempts_used"].sum()
    retry_savings = ((naive_retries - ai_retries) / max(1, naive_retries)) * 100

    print("\n" + "="*45)
    print("           SIMULATION SUMMARY RESULTS        ")
    print("="*45)
    print(f"Total Amount at Risk   : ₹{total_at_risk:,.2f}")
    print(f"AI Agent Recovered     : ₹{ai_recovered_total:,.2f} ({(ai_recovered_total/total_at_risk)*100:.1f}%)")
    print(f"Naive Baseline Recovered: ₹{naive_recovered_total:,.2f} ({(naive_recovered_total/total_at_risk)*100:.1f}%)")
    print(f"AI Retries Attempted   : {ai_retries}")
    print(f"Naive Retries Attempted: {naive_retries}")
    print(f"Wasted Retries Avoided : {retry_savings:.1f}% reduction")
    print("="*45)

if __name__ == "__main__":
    run_simulation()