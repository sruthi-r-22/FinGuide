import re
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import ScamAnalyzeResponse, OfficialSafetyResource
from backend.app.core.security import EDUCATIONAL_DISCLAIMER

SAMPLE_SCAM_SCENARIOS = [
    {
        "id": "kyc_suspension",
        "title": "Fake KYC Expiry Threat (SMS)",
        "scenario_type": "SMS Phishing",
        "message_text": "Dear Customer, your SBI account will be blocked within 24 hours due to pending KYC verification. Click http://bit.ly/sbi-kyc-update immediately to update your Aadhaar and avoid suspension.",
        "description": "Urgent SMS claiming immediate account blockage with a shortened link."
    },
    {
        "id": "fake_customer_support",
        "title": "Impersonated Bank Customer Support (Call)",
        "scenario_type": "Vishing (Voice Call)",
        "message_text": "Hello, I am calling from HDFC Bank fraud prevention department. We detected an unauthorized transaction of ₹15,000 on your card. To cancel this transaction immediately, please share the 6-digit verification code sent to your phone.",
        "description": "Caller posing as fraud department demanding an SMS OTP to 'cancel' a charge."
    },
    {
        "id": "upi_lottery_qr",
        "title": "Refund / Cashback QR Code Request",
        "scenario_type": "UPI Fraud",
        "message_text": "Congratulations! You have received a cashback refund of ₹4,999 from PhonePe. To receive the cashback directly into your account, scan this attached QR code and enter your 6-digit UPI PIN.",
        "description": "Fraudulent claim that entering a UPI PIN will receive money."
    },
    {
        "id": "apk_malware",
        "title": "Utility Bill / Electricity Disconnection APK",
        "scenario_type": "Malware / Fake App",
        "message_text": "Urgent Notice: Your electricity bill payment of last month is pending. Your power will be disconnected at 9:30 PM tonight. Please download and install our quick payment app at http://quickpay-bill-update.apk to clear the bill.",
        "description": "Threat of service disruption coercing the user to download a malicious Android APK file."
    },
    {
        "id": "fake_payment_collect",
        "title": "OLX / Marketplace Fake Buyer Collect Request",
        "scenario_type": "UPI Collect Fraud",
        "message_text": "Hi, I want to buy your sofa listed on OLX. I am an Army officer and cannot come in person. I have sent a ₹10,000 payment request on Google Pay. Click 'Approve' and enter your PIN so the advance is deposited in your account.",
        "description": "Scammer sending a debit collect request under the guise of an advance deposit."
    }
]

OFFICIAL_SAFETY_RESOURCES = [
    OfficialSafetyResource(
        name="National Cybercrime Reporting Portal (MHA / I4C)",
        contact_or_url="Helpline: 1930 | Website: https://cybercrime.gov.in",
        description="Official Government of India portal to report financial cyber fraud immediately and request transaction freeze within the golden hour."
    ),
    OfficialSafetyResource(
        name="RBI Sachet Portal",
        contact_or_url="https://sachet.rbi.org.in",
        description="RBI platform to report unauthorized financial entities, fake loan apps, and fraudulent deposit schemes."
    ),
    OfficialSafetyResource(
        name="National Cyber Coordination Centre / Chakshu",
        contact_or_url="https://sancharsaathi.gov.in/sfc/",
        description="Department of Telecommunications portal to report suspicious phone numbers, SMS, and WhatsApp spam."
    ),
    OfficialSafetyResource(
        name="Your Bank's Official Helpline",
        contact_or_url="Contact the toll-free number printed on the back of your debit card",
        description="Never search for bank customer service numbers on Google Search or unverified maps; always use the number printed on your card or official passbook."
    )
]

def analyze_message(message_text: str, scenario_type: Optional[str] = None) -> ScamAnalyzeResponse:
    text = message_text.lower()
    warning_signs = []
    suspicion_points = []
    safe_actions = []

    # 1. Check for urgency / threats
    urgency_keywords = ["within 24 hours", "blocked", "suspended", "immediately", "urgent", "tonight", "deactivated", "last warning", "expire today"]
    matched_urgency = [w for w in urgency_keywords if w in text]
    if matched_urgency:
        warning_signs.append(f"Artificial urgency tactics detected (keywords: {', '.join(matched_urgency[:2])}).")
        suspicion_points.append("Legitimate banks give official advance notices and never arbitrarily block accounts with a 24-hour ultimatum via casual SMS.")

    # 2. Check for credential requests (OTP / PIN / CVV / Password)
    if re.search(r'\b(otp|one[- ]time[- ]password|verification code|code sent|sms code)\b', text):
        warning_signs.append("Explicit or implicit request for One-Time Password (OTP) / verification code.")
        suspicion_points.append("Under RBI guidelines, no bank employee or system will ever ask a customer to reveal an OTP. An OTP is strictly meant to authenticate a debit or sensitive action.")

    if re.search(r'\b(upi[- ]pin|atm[- ]pin|enter.*pin|share.*pin)\b', text):
        warning_signs.append("Request to enter or share a UPI PIN or ATM PIN.")
        suspicion_points.append("Golden Rule of NPCI: You NEVER need to enter your UPI PIN to receive money, receive a prize, or get a refund. Entering a PIN will immediately debit funds from your bank.")

    # 3. Check for suspicious links / APK downloads
    if re.search(r'https?://|bit\.ly|tinyurl|\.apk|\.xyz|\.top|\.ru|wa\.me', text):
        warning_signs.append("Unverified link, shortened URL, or direct APK download prompt.")
        suspicion_points.append("Banks will never send third-party shortened links (bit.ly) or ask users to sideload APK files. Official applications are only distributed through Google Play Store and Apple App Store.")

    # 4. Check for impersonation / claims of authority
    authority_keywords = ["army officer", "rbi official", "customs", "police", "cyber cell", "manager", "fraud department"]
    matched_auth = [a for a in authority_keywords if a in text]
    if matched_auth:
        warning_signs.append(f"Claims of high authority or official stature ({matched_auth[0]}).")
        suspicion_points.append("Scammers frequently impersonate defense personnel, bank fraud investigators, or law enforcement to intimidate victims.")

    # 5. Check for prize / cashback lure
    if re.search(r'\b(lottery|won|cashback|refund|reward|congratulations)\b', text):
        warning_signs.append("Unsolicited reward, cashback, or lottery claim.")
        suspicion_points.append("Legitimate merchant cashbacks are credited automatically to your bank account or wallet without requiring you to approve any payment or scan a QR code.")

    # Determine risk level
    if len(warning_signs) >= 3:
        risk_level = "CRITICAL RISK — HIGH PROBABILITY OF FRAUD"
    elif len(warning_signs) >= 1:
        risk_level = "ELEVATED RISK — POTENTIAL WARNING SIGNS DETECTED"
    else:
        risk_level = "LOW RISK / UNCLEAR — PROCEED WITH VIGILANCE"
        warning_signs.append("No explicit scam keywords detected, but caution is always warranted with unsolicited messages.")
        suspicion_points.append("Always verify the sender's identity through official channels before acting.")

    # Standard safe actions
    safe_actions.append("DO NOT click any link, scan QR codes, or download attached files.")
    safe_actions.append("DO NOT share any OTP, UPI PIN, ATM PIN, or card security details with anyone.")
    safe_actions.append("Verify directly by calling the customer care number printed on the back of your physical bank debit card.")
    if "blocked" in text or "kyc" in text:
        safe_actions.append("To check your actual KYC status, log into your official net banking portal or visit your local branch in person.")
    safe_actions.append("If you suspect an attempted fraud or lost money, call the National Cybercrime Helpline at 1930 immediately.")

    why_summary = " ".join(suspicion_points) if suspicion_points else "The message contains patterns common in social engineering attempts."

    return ScamAnalyzeResponse(
        risk_level=risk_level,
        potential_warning_signs=warning_signs,
        why_suspicious=why_summary,
        safe_actions=safe_actions,
        official_safety_resources=OFFICIAL_SAFETY_RESOURCES,
        disclaimer=(
            "Educational Analysis Notice: This assessment highlights potential warning signs based on common fraud patterns. "
            "FinGuide AI does not access real telecommunication logs or guarantee conclusive authentication. "
            "Never share real passwords, OTPs, or financial credentials with any tool."
        )
    )

def get_sample_scenarios() -> List[Dict[str, Any]]:
    return SAMPLE_SCAM_SCENARIOS
