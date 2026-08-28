import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid

# Define failure scenarios, their probability of occurring, and probability of success on a naive retry
SCENARIOS = [
    {
        "code": "ERR_NETWORK_TIMEOUT",
        "reason": "Gateway timeout during authorization",
        "weight": 0.25,
        "retry_success_prob": 0.80 # High chance of success on immediate retry
    },
    {
        "code": "ERR_INSUFFICIENT_FUNDS",
        "reason": "Issuer declined: Insufficient funds in account",
        "weight": 0.30,
        "retry_success_prob": 0.30 # Low on immediate retry, needs payday logic
    },
    {
        "code": "ERR_CARD_EXPIRED",
        "reason": "Transaction declined: Card expired",
        "weight": 0.10,
        "retry_success_prob": 0.00 # Will never succeed
    },
    {
        "code": "ERR_DO_NOT_HONOR",
        "reason": "Issuer declined: Do not honor / Risk block",
        "weight": 0.15,
        "retry_success_prob": 0.05 # Rarely succeeds, risking merchant block
    },
    {
        "code": "ERR_3DS_FAILED",
        "reason": "3D Secure authentication failed or abandoned",
        "weight": 0.15,
        "retry_success_prob": 0.40 # Needs customer action
    },
    {
        "code": "ERR_DUPLICATE_TXN",
        "reason": "Duplicate transaction detected",
        "weight": 0.05,
        "retry_success_prob": 0.00 # Should never retry
    }
]

def generate_synthetic_batch(num_records=250):
    records = []
    base_time = datetime.now() - timedelta(days=2)
    
    for _ in range(num_records):
        scenario = random.choices(SCENARIOS, weights=[s["weight"] for s in SCENARIOS], k=1)[0]
        amount = round(random.uniform(100, 5000), 2)
        
        # Ground truth: Would this actually succeed if retried blindly?
        would_succeed = random.random() < scenario["retry_success_prob"]
        
        records.append({
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "merchant_id": f"merch_{random.randint(100, 999)}",
            "customer_id": f"cust_{random.randint(1000, 9999)}",
            "amount": amount,
            "currency": "INR",
            "payment_method": random.choice(["card", "upi", "netbanking"]),
            "failure_code": scenario["code"],
            "failure_reason_raw": scenario["reason"],
            "failure_timestamp": (base_time + timedelta(minutes=random.randint(1, 2880))).isoformat(),
            "customer_payment_history": random.randint(0, 15),
            "retry_attempt_number": 0,
            "would_succeed_on_retry": would_succeed # Hidden flag for evaluation
        })
        
    df = pd.DataFrame(records)
    df.to_csv("failed_payments_batch.csv", index=False)
    print(f"Generated {len(df)} records at failed_payments_batch.csv")

if __name__ == "__main__":
    generate_synthetic_batch()