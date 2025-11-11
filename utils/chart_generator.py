# utils/chart_generator.py
"""
Chart generation for Payroll Analytics Dashboard using Matplotlib.
Creates:
1. Salary Distribution per Role (Bar)
2. Average Deductions Breakdown (Pie)
3. Company Payroll Expense Over Time (Line)
"""

import os
import matplotlib.pyplot as plt
from collections import defaultdict
from utils.salary_calculator import calculate_for_employee_record

def ensure_folder(folder="static/charts"):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    return folder

def salary_distribution_chart(data):
    """Bar chart of total salary per role."""
    folder = ensure_folder()
    roles = data.get("roles", {})
    employees = data.get("employees", [])
    role_totals = defaultdict(float)

    for emp in employees:
        breakdown, _ = calculate_for_employee_record(emp, roles)
        role_totals[emp["role"]] += breakdown["grosspay"]

    roles_list = list(role_totals.keys())
    totals = [role_totals[r] for r in roles_list]

    plt.figure(figsize=(8, 5))
    plt.bar(roles_list, totals)
    plt.title("Salary Distribution per Role")
    plt.ylabel("Total Gross Pay (₹)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    path = os.path.join(folder, "salary_distribution.png")
    plt.savefig(path)
    plt.close()
    return path

def deductions_pie_chart(data):
    """Pie chart of average deduction breakdown."""
    folder = ensure_folder()
    employees = data.get("employees", [])
    roles = data.get("roles", {})

    total_pf = total_tax = total_loan = count = 0
    for emp in employees:
        breakdown, _ = calculate_for_employee_record(emp, roles)
        total_pf += breakdown["pf"]
        total_tax += breakdown["tax"]
        total_loan += breakdown["loan_debit"]
        count += 1

    avg_pf = total_pf / count
    avg_tax = total_tax / count
    avg_loan = total_loan / count

    labels = ["PF (12%)", "Tax (4%)", "Loan Debit (9%)"]
    values = [avg_pf, avg_tax, avg_loan]

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Average Deductions Breakdown")
    plt.tight_layout()
    path = os.path.join(folder, "deductions_pie.png")
    plt.savefig(path)
    plt.close()
    return path

def payroll_trend_chart(data):
    """Line chart showing company payroll expense over time."""
    folder = ensure_folder()
    history = sorted(data.get("payroll_history", []), key=lambda x: x["month"])
    if not history:
        return None

    months = [h["month"] for h in history]
    expenses = [h["total_expense"] for h in history]

    plt.figure(figsize=(8, 4))
    plt.plot(months, expenses, marker="o", linewidth=2)
    plt.title("Company Payroll Expense Over Time")
    plt.xlabel("Month")
    plt.ylabel("Total Expense (₹)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    path = os.path.join(folder, "payroll_trend.png")
    plt.savefig(path)
    plt.close()
    return path

def generate_all_charts(data):
    """Generate all charts and return their file paths."""
    return {
        "salary_distribution": salary_distribution_chart(data),
        "deductions_pie": deductions_pie_chart(data),
        "payroll_trend": payroll_trend_chart(data)
    }
