import io
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.models.schemas import ChecklistResponse, ChecklistItem
from backend.app.core.security import EDUCATIONAL_DISCLAIMER

CHECKLIST_DATA = {
    "savings_account": {
        "title": "Savings Account Opening Checklist",
        "items": [
            {
                "requirement": "Proof of Identity (POI)",
                "category": "Identity",
                "why_needed": "Mandated by RBI under PML Rules to establish customer identity. Any 1 Officially Valid Document (Passport, Voter ID, Driving Licence, or Aadhaar/e-Aadhaar).",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Rule 2(d))",
                "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Proof of Address (POA)",
                "category": "Address",
                "why_needed": "Required to verify residential address for correspondence and account records. If OVD doesn't contain current address, utility bills (<2 months old) serve as deemed OVD.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Section 16)",
                "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Permanent Account Number (PAN) or Form 60",
                "category": "Tax & Compliance",
                "why_needed": "Mandatory under Section 139A of Income-tax Act for all banking deposit accounts. If PAN is unavailable, Form 60 declaration is submitted.",
                "is_bank_dependent": False,
                "source_document": "Income Tax Rules, Rule 114B",
                "source_url": "https://incometaxindia.gov.in",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Recent Passport-Size Photographs (1 or 2 copies)",
                "category": "Personal Identification",
                "why_needed": "Affixed to physical application form and signature card for visual verification at branch.",
                "is_bank_dependent": True,
                "source_document": "SBI Customer Service Charter",
                "source_url": "https://sbi.co.in",
                "verified_status": "Standard Practice (Waived in pure eKYC/V-CIP)"
            },
            {
                "requirement": "Nomination Form (DA-1 Form)",
                "category": "Account Security",
                "why_needed": "Designates who will receive funds in the event of depositor's demise, preventing legal delays under Section 45ZA of Banking Regulation Act 1949.",
                "is_bank_dependent": False,
                "source_document": "Banking Regulation Act 1949, Section 45ZA",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "Strongly Recommended"
            },
            {
                "requirement": "Initial Deposit Amount",
                "category": "Funding",
                "why_needed": "Regular savings accounts may require an initial deposit of ₹500 - ₹3,000 depending on branch area. Note: BSBDA zero-balance accounts require ₹0.",
                "is_bank_dependent": True,
                "source_document": "Bank Product Rules",
                "source_url": "https://sbi.co.in",
                "verified_status": "Bank-Specific"
            }
        ]
    },
    "current_account": {
        "title": "Current Account Opening Checklist (Business)",
        "items": [
            {
                "requirement": "Business Registration / Incorporation Proof",
                "category": "Business Identity",
                "why_needed": "GST Certificate, Udyam Registration, Certificate of Incorporation (MCA), or Partnership Deed depending on entity constitution.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Section 28)",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Entity PAN Card",
                "category": "Tax & Compliance",
                "why_needed": "Mandatory for firms, companies, and trusts. For sole proprietorships, proprietor's personal PAN is used.",
                "is_bank_dependent": False,
                "source_document": "Income Tax Act, Section 139A",
                "source_url": "https://incometaxindia.gov.in",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "KYC of Authorized Signatories / Beneficial Owners",
                "category": "Identity",
                "why_needed": "POI and POA of all directors, partners, or trustees holding >10% ownership or control under Beneficial Ownership rules.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Rule 9)",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Board Resolution / Power of Attorney",
                "category": "Authorization",
                "why_needed": "Authorizes specific individuals to operate the current account on behalf of the company/trust.",
                "is_bank_dependent": True,
                "source_document": "Companies Act 2013 / Bank Rules",
                "source_url": "https://mca.gov.in",
                "verified_status": "Entity-Specific"
            },
            {
                "requirement": "Initial Deposit & Minimum Average Balance Agreement",
                "category": "Funding",
                "why_needed": "Current accounts typically mandate maintaining an Average Monthly Balance (AMB) ranging from ₹10,000 to ₹1,00,000 depending on package.",
                "is_bank_dependent": True,
                "source_document": "Bank Commercial Schedule",
                "source_url": "https://sbi.co.in",
                "verified_status": "Bank-Specific"
            }
        ]
    },
    "kyc_requirements": {
        "title": "Understanding Standard KYC Requirements",
        "items": [
            {
                "requirement": "One Officially Valid Document (OVD)",
                "category": "Identity & Address",
                "why_needed": "Choose ANY ONE from: 1. Passport, 2. Driving Licence, 3. Aadhaar / Masked e-Aadhaar, 4. Voter ID, 5. NREGA Job Card, 6. NPR Letter.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC",
                "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Aadhaar eKYC Consent Form (Digital Onboarding)",
                "category": "Digital Verification",
                "why_needed": "Explicit voluntary consent required to fetch demographic details and photo from UIDAI repository.",
                "is_bank_dependent": False,
                "source_document": "Aadhaar Act, Section 11A",
                "source_url": "https://uidai.gov.in",
                "verified_status": "Statutory Requirement"
            },
            {
                "requirement": "Live Video Interaction (V-CIP)",
                "category": "Remote Verification",
                "why_needed": "Geo-tagged video verification with bank officer, live liveliness check, and PAN card presentation for branchless onboarding.",
                "is_bank_dependent": True,
                "source_document": "RBI Master Direction on V-CIP Guidelines",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "Digital Channel Only"
            }
        ]
    },
    "kyc_update": {
        "title": "Updating Periodic KYC Details Checklist",
        "items": [
            {
                "requirement": "Self-Declaration (If No Change in Details)",
                "category": "Periodic Refresh",
                "why_needed": "For low and medium risk customers with no changes in address or status, RBI allows simple self-declaration via Net Banking, Mobile App, or email without fresh documents.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Section 38)",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "RBI Regulation"
            },
            {
                "requirement": "Updated Address Document (If Address Changed)",
                "category": "Address Refresh",
                "why_needed": "Submit updated OVD or deemed OVD (utility bill <2 months old, bank statement) via branch, web portal, or digital self-service.",
                "is_bank_dependent": False,
                "source_document": "RBI Master Direction on KYC (Section 38)",
                "source_url": "https://www.rbi.org.in",
                "verified_status": "RBI Regulation"
            },
            {
                "requirement": "Warning: Safe KYC Update Method",
                "category": "Security Protocol",
                "why_needed": "NEVER click links in SMS or install third-party APK apps to update KYC. Only update inside official bank apps or branches.",
                "is_bank_dependent": False,
                "source_document": "RBI Public Advisory on KYC Fraud",
                "source_url": "https://rbi.org.in",
                "verified_status": "Critical Safety Protocol"
            }
        ]
    },
    "digital_banking": {
        "title": "Digital Banking Registration Checklist (UPI & Net Banking)",
        "items": [
            {
                "requirement": "Registered Mobile Number (RMN) Active SIM",
                "category": "Authentication",
                "why_needed": "Your phone must contain the active SIM card registered with your bank account to send SMS device binding tokens for UPI and Mobile Banking.",
                "is_bank_dependent": False,
                "source_document": "NPCI UPI Operating Regulations",
                "source_url": "https://www.npci.org.in",
                "verified_status": "NPCI Security Requirement"
            },
            {
                "requirement": "Active Debit Card with PIN / Aadhaar OTP",
                "category": "Credential Creation",
                "why_needed": "Used to verify your identity when setting up your 4 or 6 digit UPI PIN or initial Net Banking login password.",
                "is_bank_dependent": False,
                "source_document": "NPCI UPI PIN Onboarding Framework",
                "source_url": "https://www.npci.org.in",
                "verified_status": "NPCI Security Requirement"
            },
            {
                "requirement": "Customer ID / CIF Number",
                "category": "Account Profile",
                "why_needed": "Printed on your bank passbook or statement, required to activate internet banking profile for the first time.",
                "is_bank_dependent": True,
                "source_document": "Bank Net Banking Registration Manual",
                "source_url": "https://sbi.co.in",
                "verified_status": "Bank-Specific"
            }
        ]
    }
}

def get_checklist(task: str, bank: Optional[str] = None) -> ChecklistResponse:
    key = task.lower().strip()
    data = CHECKLIST_DATA.get(key, CHECKLIST_DATA["savings_account"])
    
    items = []
    for it in data["items"]:
        # If user specifically asked for SBI and item is bank dependent, customize
        requirement = it["requirement"]
        why = it["why_needed"]
        if bank and bank.lower() == "sbi":
            if "Initial Deposit Amount" in requirement:
                why += " (Note: SBI has waived minimum balance penalties for regular savings accounts since 2020)."
        items.append(ChecklistItem(**it))

    return ChecklistResponse(
        task=key,
        task_title=data["title"] + (f" ({bank.upper()})" if bank else ""),
        bank=bank,
        items=items,
        disclaimer=EDUCATIONAL_DISCLAIMER
    )

def generate_pdf_bytes(checklist_resp: ChecklistResponse) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ChecklistTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0B132B')
    )
    
    meta_style = ParagraphStyle(
        'ChecklistMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#FFFFFF')
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    )

    story.append(Paragraph(f"FinGuide AI — {checklist_resp.task_title}", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Educational Banking Document Checklist</b> | Grounded in official RBI & NPCI guidelines", meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3A86FF'), spaceBefore=4, spaceAfter=12))

    # Table content
    data = [[
        Paragraph("Requirement", table_header_style),
        Paragraph("Category", table_header_style),
        Paragraph("Why Needed & Verification Status", table_header_style),
        Paragraph("Official Source", table_header_style)
    ]]

    for it in checklist_resp.items:
        why_text = f"<b>{it.why_needed}</b><br/><font color='#059669'>[{it.verified_status}]</font>"
        source_text = f"{it.source_document}"
        data.append([
            Paragraph(f"<b>{it.requirement}</b>", table_cell_style),
            Paragraph(it.category, table_cell_style),
            Paragraph(why_text, table_cell_style),
            Paragraph(source_text, table_cell_style)
        ])

    table = Table(data, colWidths=[120, 75, 230, 115])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B132B')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')])
    ]))

    story.append(table)
    story.append(Spacer(1, 16))
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B')
    )
    story.append(Paragraph(checklist_resp.disclaimer, disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
