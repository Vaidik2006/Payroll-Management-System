# utils/pdf_generator.py
"""
Generate a PDF payslip using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import date
import os

def generate_payslip_pdf(employee: dict, breakdown: dict, output_folder: str = "static/payslips") -> str:
    """Generate a professional-looking PDF payslip and return file path."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    filename = f"Payslip_{employee['name'].replace(' ', '_')}_{date.today().strftime('%b_%Y')}.pdf"
    filepath = os.path.join(output_folder, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.setTitle("Payslip")

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "Company Payroll Payslip")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Date: {date.today().strftime('%d %B %Y')}")

    # Employee Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 110, "Employee Details:")
    c.setFont("Helvetica", 10)
    y = height - 130
    details = [
        ("Name", employee["name"]),
        ("Employee Code", employee["code"]),
        ("Role", employee["role"]),
        ("Experience", f"{employee['exp']} years"),
        ("Working Hours", f"{breakdown['hours']} Hrs"),
        ("Hourly Rate", f"₹{breakdown['hourly_rate']}"),
    ]
    for key, val in details:
        c.drawString(50, y, f"{key}: {val}")
        y -= 15

    # Earnings
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Earnings")
    y -= 20
    c.setFont("Helvetica", 10)
    earnings = [
        ("Basic Pay", breakdown["basic"]),
        ("HRA (27%)", breakdown["hra"]),
        ("DA (120%)", breakdown["da"]),
        ("Meal Allowance", breakdown["meal_allowance"]),
        ("Medical Allowance", breakdown["medical_allowance"]),
        ("Transport Allowance", breakdown["transport_allowance"]),
    ]
    for key, val in earnings:
        c.drawString(50, y, f"{key}")
        c.drawRightString(width - 60, y, f"₹{val}")
        y -= 15

    # Deductions
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Deductions")
    y -= 20
    c.setFont("Helvetica", 10)
    deductions = [
        ("PF (12%)", breakdown["pf"]),
        ("Tax (4%)", breakdown["tax"]),
        ("Loan Debit", breakdown["loan_debit"]),
    ]
    for key, val in deductions:
        c.drawString(50, y, f"{key}")
        c.drawRightString(width - 60, y, f"₹{val}")
        y -= 15

    # Net Pay
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Net Pay:")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 60, y, f"₹{breakdown['netpay']}")

    # Footer
    y -= 50
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, y, "This is a computer-generated payslip and does not require a signature.")

    c.showPage()
    c.save()
    return filepath
