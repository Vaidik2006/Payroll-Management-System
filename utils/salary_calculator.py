# utils/salary_calculator.py
"""
Enhanced Salary Calculator
- Includes role-based rate (from roles.json)
- Adds experience-based increment scaling
- Mirrors C++ logic for allowances/deductions
"""

# Base constants (from your C++ code)
TAX_RATE = 0.04
DA_RATE = 1.20
PF_RATE = 0.12
HRA_RATE = 0.27
LOAN_DEBIT_RATE = 0.09
MEAL_ALLOWANCE = 300
MEDICAL_ALLOWANCE = 300
TRANSPORT_ALLOWANCE = 300

def experience_multiplier(exp: int) -> float:
    """Return salary increment factor based on years of experience."""
    if exp <= 1:
        return 1.00   # no increment
    elif exp <= 3:
        return 1.05   # +5%
    elif exp <= 5:
        return 1.10   # +10%
    elif exp <= 7:
        return 1.15   # +15%
    else:
        return 1.20   # +20%

def calculate_pay_from_hours(hours: int, loan_balance: int = 0, hourly_rate: float = 300.0, exp: int = 0):
    """
    Calculate salary breakdown given monthly hours, role rate, experience, and loan balance.
    Returns breakdown dictionary with gross and net pay.
    """
    # Apply experience-based multiplier
    rate_with_exp = hourly_rate * experience_multiplier(exp)

    # Base pay
    basic = int(hours * rate_with_exp)

    # Allowances and deductions (same as your C++ logic)
    tax = int(TAX_RATE * basic)
    da = int(DA_RATE * basic)
    pf = int(PF_RATE * basic)
    hra = int(HRA_RATE * basic)

    meal = MEAL_ALLOWANCE
    medical = MEDICAL_ALLOWANCE
    transport = TRANSPORT_ALLOWANCE

    loan_debit = int(LOAN_DEBIT_RATE * basic)
    if loan_debit > loan_balance:
        loan_debit = loan_balance
    loan_balance_after = int(loan_balance - loan_debit)

    grosspay = int((basic + meal + medical + transport + hra + da) - (pf + tax + loan_debit))
    netpay = grosspay

    return {
        "hours": int(hours),
        "hourly_rate": int(hourly_rate),
        "effective_rate": int(rate_with_exp),
        "exp_multiplier": round(experience_multiplier(exp), 2),
        "basic": basic,
        "hra": hra,
        "da": da,
        "pf": pf,
        "tax": tax,
        "meal_allowance": meal,
        "medical_allowance": medical,
        "transport_allowance": transport,
        "loan_debit": loan_debit,
        "loan_balance_after": loan_balance_after,
        "grosspay": grosspay,
        "netpay": netpay
    }

def calculate_for_employee_record(emp_record: dict, roles_dict: dict = None):
    """Calculate and update salary for an employee record (role + experience aware)."""
    role = emp_record.get("role", "")
    exp = int(emp_record.get("exp", 0))
    hours = int(emp_record.get("working_hours", 0))
    loan_balance = int(emp_record.get("loan_balance", 0))

    # Get role hourly rate (fallback to 300)
    hourly_rate = 300.0
    if roles_dict and role in roles_dict:
        hourly_rate = float(roles_dict[role].get("hourly_rate", 300))

    breakdown = calculate_pay_from_hours(
        hours=hours,
        loan_balance=loan_balance,
        hourly_rate=hourly_rate,
        exp=exp
    )

    updated = emp_record.copy()
    updated.update({
        "salary": breakdown["basic"],
        "hra": breakdown["hra"],
        "da": breakdown["da"],
        "pf": breakdown["pf"],
        "tax": breakdown["tax"],
        "meal_allowance": breakdown["meal_allowance"],
        "medical_allowance": breakdown["medical_allowance"],
        "transport_allowance": breakdown["transport_allowance"],
        "loan_debit": breakdown["loan_debit"],
        "loan_balance": breakdown["loan_balance_after"],
        "grosspay": breakdown["grosspay"],
        "effective_rate": breakdown["effective_rate"]
    })
    return breakdown, updated
