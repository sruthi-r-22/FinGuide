from backend.app.core.security import detect_sensitive_credentials, sanitize_user_input

def test_card_number_detection():
    text = "My debit card number is 4111 2222 3333 4444 please check balance"
    has_sensitive, reasons = detect_sensitive_credentials(text)
    assert has_sensitive is True
    assert any("card number" in r.lower() for r in reasons)

def test_otp_detection():
    text = "My OTP is: 489291"
    has_sensitive, reasons = detect_sensitive_credentials(text)
    assert has_sensitive is True
    assert any("one-time password" in r.lower() for r in reasons)

def test_pin_detection():
    text = "Is my upi-pin: 1234 safe to tell callers?"
    has_sensitive, reasons = detect_sensitive_credentials(text)
    assert has_sensitive is True
    assert any("pin" in r.lower() for r in reasons)

def test_safe_banking_question():
    text = "What documents are required to open a regular savings bank account?"
    has_sensitive, reasons = detect_sensitive_credentials(text)
    assert has_sensitive is False
    assert len(reasons) == 0

def test_sanitize_excessive_length():
    huge_text = "What is KYC? " * 500
    cleaned = sanitize_user_input(huge_text)
    assert len(cleaned) <= 2000
