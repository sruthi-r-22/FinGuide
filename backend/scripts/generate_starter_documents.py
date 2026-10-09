import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0B132B')
)

h2_style = ParagraphStyle(
    'DocH2',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#1C2541'),
    spaceBefore=10,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#1E293B'),
    spaceAfter=6
)

callout_style = ParagraphStyle(
    'DocCallout',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#065F46'),
    backColor=colors.HexColor('#ECFDF5'),
    borderPadding=6,
    spaceBefore=6,
    spaceAfter=6
)

def build_pdf(filepath, title, meta_lines, sections):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 4))
    
    for m in meta_lines:
        story.append(Paragraph(f"<b>{m[0]}:</b> {m[1]}", body_style))
    
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3A86FF'), spaceBefore=4, spaceAfter=10))
    
    for sec_title, sec_paragraphs in sections:
        if sec_title:
            story.append(Paragraph(sec_title, h2_style))
        for p in sec_paragraphs:
            if p.startswith("[SAFETY NOTICE]") or p.startswith("[OFFICIAL RULE]"):
                story.append(Paragraph(p, callout_style))
            else:
                story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    print(f"Generated: {filepath}")

def generate_rbi_kyc():
    filepath = os.path.join(DOCUMENTS_DIR, "RBI_KYC_Master_Directions_Summary.pdf")
    title = "Reserve Bank of India — Master Direction on Know Your Customer (KYC)"
    meta = [
        ("Issuing Authority", "Reserve Bank of India (Department of Regulation)"),
        ("Reference", "RBI/DBR/2015-16/18 Master Direction DBR.AML.BC.No.81/14.01.001/2015-16"),
        ("Subject", "Officially Valid Documents (OVD), eKYC, and Periodic KYC Updates"),
        ("Last Verified", "October 2024 (Consolidated Directions)")
    ]
    sections = [
        ("1. Purpose and Scope of KYC", [
            "Know Your Customer (KYC) guidelines require regulated entities (banks, NBFCs, payment system providers) to establish the true identity and address of customers prior to opening accounts or establishing business relationships.",
            "The overarching objectives are to prevent identity fraud, curb money laundering, combat financing of terrorism, and ensure customer asset security."
        ]),
        ("2. Officially Valid Documents (OVDs) for Individuals", [
            "For opening a standard individual savings or current bank account, an individual customer must provide one Officially Valid Document (OVD) that serves as proof of identity and proof of address.",
            "As defined under Rule 2(d) of the PML Rules and RBI Master Direction, the following 6 documents are designated as Officially Valid Documents (OVDs):",
            "1. Passport (valid with photograph)",
            "2. Driving Licence (issued by Regional Transport Office)",
            "3. Proof of possession of Aadhaar number (Aadhaar card/e-Aadhaar in offline verification or masked format)",
            "4. Voter's Identity Card (issued by the Election Commission of India)",
            "5. Job card issued by NREGA (duly signed by an officer of the State Government)",
            "6. Letter issued by the National Population Register (NPR) containing details of name and address.",
            "Note: PAN card or Form 60 is mandatory for financial transactions and tax compliance under Section 139A of the Income-tax Act, but PAN without address is proof of identity only."
        ]),
        ("3. Central KYC Registry (CKYC) and KIN", [
            "Regulated entities are mandated to upload KYC records of individual customers to the Central KYC Records Registry (CKYCR) managed by CERSAI within 3 days of onboarding.",
            "Once uploaded, a unique 14-digit KYC Identifier (KIN) is generated. When a customer opens an account or investment with another regulated financial entity, they can simply quote their 14-digit KIN without resubmitting physical documents."
        ]),
        ("4. Aadhaar eKYC and Video KYC (V-CIP)", [
            "Aadhaar-based eKYC can be performed via biometric authentication or OTP verification with customer consent. OTP-based e-KYC accounts are subject to certain initial transaction limits and must complete full verification within one year.",
            "Video-based Customer Identification Process (V-CIP) is an RBI-approved digital procedure that allows bank officials to perform live audio-visual verification with geo-tagging, live photograph matching, and Aadhaar/PAN validation without requiring a physical branch visit."
        ]),
        ("5. Periodic KYC Updates and Risk Categorization", [
            "Banks categorize accounts based on risk: High Risk, Medium Risk, and Low Risk.",
            "Periodic KYC update must be carried out at least once every 2 years for high risk customers, once every 8 years for medium risk customers, and once every 10 years for low risk customers.",
            "For low-risk customers, if there is no change in KYC information, a simple self-declaration submitted via internet banking, mobile app, email, or post is legally sufficient without re-submitting fresh documents."
        ]),
        ("6. Crucial Consumer Safety Warning", [
            "[SAFETY NOTICE] RBI Warning: Banks never send SMS, WhatsApp messages, or emails asking customers to click on unverified links or download APK files to update their KYC. Legitimate periodic updates are conducted strictly through official bank branches, authenticated mobile banking portals, or authorized net banking sessions."
        ])
    ]
    build_pdf(filepath, title, meta, sections)

def generate_rbi_customer_protection():
    filepath = os.path.join(DOCUMENTS_DIR, "RBI_Customer_Protection_Limiting_Liability.pdf")
    title = "Reserve Bank of India — Customer Protection: Limiting Liability in Unauthorized Electronic Transactions"
    meta = [
        ("Issuing Authority", "Reserve Bank of India (Department of Banking Regulation)"),
        ("Circular Reference", "RBI/2017-18/15 DBR.No.Leg.BC.78/09.07.005/2017-18"),
        ("Applicability", "Commercial Banks, Small Finance Banks, Payment Banks"),
        ("Effective Date", "July 6, 2017 (In active force)")
    ]
    sections = [
        ("1. Framework for Customer Protection", [
            "With increased reliance on electronic payments, the RBI established clear rules determining customer liability in cases of unauthorized electronic banking transactions (third-party breaches, card skimming, phishing, and remote compromises)."
        ]),
        ("2. Zero Liability of a Customer", [
            "A customer has ZERO LIABILITY in the following circumstances:",
            "Case A (Contributory Fraud): Where the fraud, negligence, or deficiency is on the part of the bank (irrespective of whether the transaction was reported by the customer or not).",
            "Case B (Third-Party Breach): Where the deficiency lies neither with the bank nor with the customer, but lies elsewhere in the system, AND the customer notifies the bank within THREE WORKING DAYS of receiving the communication from the bank regarding the unauthorized transaction."
        ]),
        ("3. Limited Liability of a Customer", [
            "If the responsibility for the unauthorized transaction lies neither with the bank nor with the customer (third-party compromise), and the customer reports the transaction with a delay of FOUR TO SEVEN WORKING DAYS after receiving the bank alert:",
            "- Basic Savings Bank Deposit Account (BSBDA): Maximum liability is capped at ₹5,000.",
            "- Other Savings Accounts / Prepaid Instruments / Credit Cards with limit up to ₹5 Lakh: Maximum liability is capped at ₹10,000.",
            "- Current / Cash Credit / Overdraft Accounts / Credit Cards with limit above ₹5 Lakh: Maximum liability is capped at ₹25,000.",
            "If reported beyond 7 working days, liability is determined per the bank's Board-approved policy."
        ]),
        ("4. Customer's Full Liability", [
            "[OFFICIAL RULE] Where the loss is due to negligence by the customer, such as where they have shared payment credentials (e.g. sharing OTP, UPI PIN, ATM PIN, or Internet Banking password with callers or phishing sites), the customer will bear the entire loss until they report the unauthorized transaction to the bank. Any loss occurring AFTER reporting the transaction to the bank must be borne by the bank."
        ]),
        ("5. Mandatory Reversal Timeline", [
            "Upon customer notification of an unauthorized transaction, the bank must credit (shadow reversal) the amount involved in the unauthorized transaction to the customer's account within 10 WORKING DAYS from the date of notification.",
            "The bank must ensure that the complaint is resolved and customer liability, if any, is established within a maximum period not exceeding 90 days from receipt of complaint."
        ])
    ]
    build_pdf(filepath, title, meta, sections)

def generate_npci_upi_guidelines():
    filepath = os.path.join(DOCUMENTS_DIR, "NPCI_UPI_Safety_and_Operating_Guidelines.pdf")
    title = "National Payments Corporation of India — UPI Safety & Operating Guidelines"
    meta = [
        ("Issuing Organization", "National Payments Corporation of India (NPCI)"),
        ("System", "Unified Payments Interface (UPI)"),
        ("Topic", "Consumer Protection, Operating Mechanics, and Golden Rules"),
        ("Publication", "NPCI Consumer Awareness & Safety Charter 2023-2024")
    ]
    sections = [
        ("1. What is Unified Payments Interface (UPI)?", [
            "UPI is an instant real-time payment system developed by NPCI that enables peer-to-peer (P2P) and person-to-merchant (P2M) transactions across different banks using a single mobile application.",
            "Transactions are settled instantly 24 hours a day, 7 days a week, 365 days a year using the underlying IMPS infrastructure."
        ]),
        ("2. The Golden Rule of UPI PIN", [
            "[SAFETY NOTICE] THE GOLDEN RULE OF UPI: UPI PIN is entered ONLY to DEBIT money from your bank account (to send money, pay a merchant, or check your account balance). YOU NEVER NEED TO ENTER YOUR UPI PIN TO RECEIVE MONEY OR CLAIM A REFUND OR PRIZE.",
            "If someone claims they are sending you money, a cashback, or refund, and asks you to 'scan a QR code' or 'enter your UPI PIN', IT IS A FRAUDULENT SCAM. Receiving money requires NO PIN whatsoever."
        ]),
        ("3. Push vs Collect (Pull) Requests", [
            "In a 'Push' transaction, the payer initiates the payment directly to the recipient's Virtual Payment Address (VPA) or scanned QR code.",
            "In a 'Collect' (Pull) request, a merchant or individual requests payment from you. The UPI application will display the requester's name, requested amount, and an option to 'Approve' or 'Decline'.",
            "Always inspect the requester identity carefully before approving collect requests. Never approve collect requests received from unknown senders."
        ]),
        ("4. Transaction Limits and Operating Safeguards", [
            "Standard P2P UPI daily transaction limit is set at ₹1,00,000 per day by default, though individual banks may configure lower internal limits.",
            "Enhanced limits of up to ₹5,00,000 per transaction are permitted for specific verified categories: Hospital bills, Educational institutions, IPO subscriptions, and RBI Retail Direct government securities purchases.",
            "Users can view the verified name registered with the receiving bank before confirming the payment."
        ]),
        ("5. Online Dispute Resolution (ODR)", [
            "If a transaction fails or funds are debited without reaching the beneficiary, the NPCI UPI auto-reversal mechanism triggers an immediate refund within T+1 working days.",
            "Customers can register disputes directly in-app using the UPI Auto-Dispute Resolution (ODR) feature or through their issuing bank's mobile portal."
        ])
    ]
    build_pdf(filepath, title, meta, sections)

def generate_sbi_savings_guide():
    filepath = os.path.join(DOCUMENTS_DIR, "SBI_Savings_Account_Rules_and_Services.pdf")
    title = "State Bank of India — Savings Bank Account Rules, Requirements & Services Guide"
    meta = [
        ("Bank", "State Bank of India (Public Sector Bank)"),
        ("Product", "Regular Savings Bank Account & BSBDA"),
        ("Regulatory Oversight", "Reserve Bank of India Guidelines"),
        ("Updated Terms", "Annual Customer Service Charter (Current Rules)")
    ]
    sections = [
        ("1. Savings Account Types & Eligibility", [
            "Any resident individual (single, joint, or guardian on behalf of minor) can open a Savings Bank Account.",
            "A Regular Savings Account allows unlimited deposits, debit card access, internet/mobile banking, and chequebook issuance.",
            "A Basic Savings Bank Deposit Account (BSBDA) is an entry-level zero-balance financial inclusion account that does not require any minimum initial deposit or monthly balance maintenance."
        ]),
        ("2. Required Documentation for Account Opening", [
            "For opening a Savings Account at SBI or any major Indian public sector bank, the following documents are required:",
            "1. One Recent Passport Size Photograph (signed across).",
            "2. Proof of Identity: One Officially Valid Document (Passport, Voter ID, Driving Licence, Aadhaar / Masked e-Aadhaar, NREGA Job Card).",
            "3. Proof of Address: If the OVD does not contain the updated address, documents such as utility bill (electricity, telephone, water bill not older than 2 months), property tax receipt, or bank statement can be used as deemed OVD for 3 months pending update.",
            "4. Permanent Account Number (PAN) or Form 60/61 if PAN is not yet allotted."
        ]),
        ("3. Minimum Average Balance (MAB) Waiver", [
            "State Bank of India has WAIVED all Minimum Average Balance (MAB / AMB) charges across all Regular Savings Bank Accounts since March 2020.",
            "Customers maintaining regular savings accounts are NOT penalized with non-maintenance charges if the balance falls below previous thresholds (metro: ₹3,000, semi-urban: ₹2,000, rural: ₹1,000).",
            "However, certain specialized premium tier accounts (e.g., Wealth, Privilege accounts) may have product-specific average quarterly balance covenants."
        ]),
        ("4. Nomination Facility (Section 45ZA)", [
            "Nomination is strongly advised when opening an account under Section 45ZA of the Banking Regulation Act, 1949.",
            "Nomination ensures that in the event of the depositor's demise, the balance in the account can be released to the registered nominee without demanding succession certificates or court letters of administration, protecting the interests of the rightful legal beneficiaries."
        ]),
        ("5. Safe Banking Practices", [
            "[SAFETY NOTICE] Always keep your mobile number updated with your home branch to receive instant SMS alerts for all credits and debits. Report any unrecognized debit transaction immediately to SBI toll-free customer helpline 1800 1234 or national cybercrime helpline 1930."
        ])
    ]
    build_pdf(filepath, title, meta, sections)

if __name__ == "__main__":
    generate_rbi_kyc()
    generate_rbi_customer_protection()
    generate_npci_upi_guidelines()
    generate_sbi_savings_guide()
    print("All starter documents generated successfully!")
