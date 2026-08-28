import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is missing from environment variables or .env file.")

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are 'Retry Brain', an intelligent payment recovery agent for a payment gateway.
Your task is to analyze failed payment metadata, classify the root cause, and determine a targeted recovery strategy.

Enforce the following guidelines:
1. Network / Gateway timeouts -> Immediate automated retry (1-2 attempts).
2. Insufficient funds -> Delayed retry with customer notification (recommend retry delay 24-72 hrs).
3. Expired / Invalid card -> Trigger method update prompt (0 retries allowed).
4. Bank / Issuer hard declines (do-not-honor, stolen card, risk block) -> Do NOT retry. Abort or escalate.
5. 3DS / OTP failures -> Immediate retry option with prompt to complete OTP.

You MUST return strictly valid JSON matching this exact schema:
{
    "root_cause_category": "string (e.g., Network Error, Insufficient Funds, Expired Card, Issuer Decline, OTP Failure)",
    "recommended_action": "string (one of: IMMEDIATE_RETRY, DELAYED_RETRY_NOTIFY, NOTIFY_UPDATE_METHOD, ABORT, ESCALATE_MANUAL)",
    "retry_delay_hours": integer (0 if immediate or abort),
    "max_attempts_allowed": integer (0 to 3),
    "confidence": float (0.0 to 1.0),
    "reasoning": "string (One concise sentence explaining the decision for audit logs)"
}
"""

def evaluate_failure(transaction_data: dict) -> dict:
    """
    Analyzes transaction failure metadata using GPT-OSS via Groq 
    and returns a structured recovery strategy.
    """
    prompt = f"Analyze this failed transaction:\n{json.dumps(transaction_data, indent=2)}"
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw_output = response.choices[0].message.content
        return json.loads(raw_output)
        
    except Exception as e:
        print(f"Error processing transaction {transaction_data.get('transaction_id')}: {e}")
        # Safe default fallback if API call fails
        return {
            "root_cause_category": "Unknown Error",
            "recommended_action": "ABORT",
            "retry_delay_hours": 0,
            "max_attempts_allowed": 0,
            "confidence": 0.0,
            "reasoning": f"Execution fallback triggered due to error: {str(e)}"
        }

if __name__ == "__main__":
    # Quick standalone sanity test
    sample_txn = {
        "transaction_id": "txn_test_001",
        "amount": 2999.0,
        "failure_code": "ERR_INSUFFICIENT_FUNDS",
        "failure_reason_raw": "Issuer declined: Insufficient funds in account",
        "payment_method": "upi"
    }
    
    print("Testing Decision Engine with sample failed transaction...")
    decision = evaluate_failure(sample_txn)
    print("\nDecision Output:")
    print(json.dumps(decision, indent=2))