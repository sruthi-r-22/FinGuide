import re
from typing import Tuple, List

# Patterns for sensitive financial credentials
CARD_PATTERN = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b')
CVV_PATTERN = re.compile(r'\b(?:cvv|cvc|security code)(?:\s+is|\s*[:=-])?\s*[:=]?\s*(\d{3,4})\b', re.IGNORECASE)
OTP_PATTERN = re.compile(r'\b(?:otp|one[- ]time[- ]password|verification code)(?:\s+is|\s*[:=-])?\s*[:=]?\s*(\d{4,8})\b', re.IGNORECASE)
PIN_PATTERN = re.compile(r'\b(?:upi[- ]pin|atm[- ]pin|mpin|pin)(?:\s+is|\s*[:=-])?\s*[:=]?\s*(\d{4,6})\b', re.IGNORECASE)
PASSWORD_PATTERN = re.compile(r'\b(?:netbanking password|login password|password)(?:\s+is|\s*[:=-])?\s*[:=]?\s*([^\s,]{6,})\b', re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')

# Prohibited sensitive instructions or attempts to transact
TRANSACTION_ATTEMPT_KEYWORDS = [
    "transfer money from my account",
    "send 1000 rupees",
    "debit my account",
    "check my actual balance",
    "withdraw cash",
    "link my bank account",
    "buy this stock",
    "recommend which mutual fund to invest"
]

def detect_sensitive_credentials(text: str) -> Tuple[bool, List[str]]:
    """
    Scans input text for sensitive banking credentials.
    Returns (has_sensitive_data, list_of_warning_reasons).
    Does NOT log the sensitive input.
    """
    reasons = []
    
    if CARD_PATTERN.search(text):
        reasons.append("Potential 16-digit debit/credit card number detected.")
        
    if CVV_PATTERN.search(text):
        reasons.append("CVV/CVC security code pattern detected.")
        
    if OTP_PATTERN.search(text):
        reasons.append("One-Time Password (OTP) pattern detected.")
        
    if PIN_PATTERN.search(text):
        reasons.append("UPI PIN or ATM PIN pattern detected.")
        
    if PASSWORD_PATTERN.search(text):
        reasons.append("Banking password credential pattern detected.")
        
    if AADHAAR_PATTERN.search(text):
        reasons.append("Full 12-digit Aadhaar number detected.")

    return (len(reasons) > 0, reasons)

def sanitize_user_input(text: str) -> str:
    """
    Truncates excessive input length to prevent denial-of-service or token flooding.
    """
    max_len = 2000
    cleaned = text.strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned

EDUCATIONAL_DISCLAIMER = (
    "Disclaimer: FinGuide AI is an educational guidance assistant designed to explain public banking "
    "procedures, terms, and digital safety rules. It does not access bank accounts, execute transactions, "
    "or provide individual investment advice. For specific account actions, always consult your official bank branch or portal."
)
