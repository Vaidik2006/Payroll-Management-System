from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
import datetime
import random

from utils.data_handler import add_employee, delete_employee
from utils.chart_generator import generate_all_charts
from utils.pdf_generator import generate_payslip_pdf
from utils.data_handler import load_data, save_data, find_employee_by_username, find_employee_by_code, update_employee
from utils.salary_calculator import calculate_for_employee_record

app = Flask(__name__)
app.secret_key = "vaidy-payroll-key"  # change later for production

# Folder setup for generated files
if not os.path.exists("static/payslips"):
    os.makedirs("static/payslips", exist_ok=True)
if not os.path.exists("static/charts"):
    os.makedirs("static/charts", exist_ok=True)

# ---------------------- ROUTES ----------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------------- LOGIN ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        data = load_data()
        # Admin login
        admin = data.get("logins", {}).get("admin", {})
        if username == admin.get("username") and password == admin.get("password"):
            session['user_role'] = 'admin'
            session['username'] = username
            return redirect(url_for('admin_dashboard'))

        # Employee login
        emp = find_employee_by_username(data, username)
        if emp and emp.get("password") == password:
            session['user_role'] = 'employee'
            session['username'] = username
            session['emp_code'] = emp.get("code")
            return redirect(url_for('employee_dashboard'))

        flash("Invalid username or password!", "error")
        return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------- ADMIN DASHBOARD ----------------------
@app.route('/admin')
def admin_dashboard():
    if 'user_role' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    data = load_data()
    employees = data.get("employees", [])
    roles = data.get("roles", {})

    # --- Build data for charts ---
    from collections import defaultdict
    role_totals = defaultdict(float)
    total_pf = total_tax = total_loan = 0
    months, expenses = [], []

    for emp in employees:
        breakdown, _ = calculate_for_employee_record(emp, roles)
        role_totals[emp["role"]] += breakdown["grosspay"]
        total_pf += breakdown["pf"]
        total_tax += breakdown["tax"]
        total_loan += breakdown["loan_debit"]

    count = len(employees)
    payroll_history = sorted(data.get("payroll_history", []), key=lambda x: x["month"])
    for h in payroll_history:
        months.append(h["month"])
        expenses.append(h["total_expense"])

    charts_data = {
        "roles": list(role_totals.keys()),
        "roleTotals": list(role_totals.values()),
        "avgPF": round(total_pf / count, 2),
        "avgTax": round(total_tax / count, 2),
        "avgLoan": round(total_loan / count, 2),
        "months": months,
        "expenses": expenses
    }

    return render_template(
        'admin_dashboard.html',
        employees=employees,
        roles=roles,
        charts_data=charts_data
    )


# ---------------------- EMPLOYEE DASHBOARD ----------------------
@app.route('/employee')
def employee_dashboard():
    if 'user_role' not in session or session['user_role'] != 'employee':
        return redirect(url_for('login'))

    data = load_data()
    emp = find_employee_by_username(data, session['username'])
    if not emp:
        return redirect(url_for('logout'))

    # Auto calculate salary for this month
    breakdown, updated = calculate_for_employee_record(emp, roles_dict=data.get("roles", {}))
    update_employee(data, updated)
    save_data(data)
    return render_template('employee_dashboard.html', employee=updated, breakdown=breakdown)

# ---------------------- VIEW PAYSLIP (HTML VERSION) ----------------------
@app.route('/payslip/<int:emp_code>')
def payslip_view(emp_code):
    data = load_data()
    emp = find_employee_by_code(data, emp_code)
    if not emp:
        flash("Employee not found!", "error")
        return redirect(url_for('admin_dashboard'))

    breakdown, _ = calculate_for_employee_record(emp, roles_dict=data.get("roles", {}))
    pdf_path = generate_payslip_pdf(emp, breakdown)
    pdf_filename = os.path.basename(pdf_path)

    return render_template(
        'payslip.html',
        employee=emp,
        breakdown=breakdown,
        date=datetime.date.today(),
        pdf_filename=pdf_filename
    )

# ---------------------- ADD EMPLOYEE ----------------------
@app.route("/employee/add", methods=["GET", "POST"])
def add_employee_route():
    if 'user_role' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    data = load_data()
    roles = list(data.get("roles", {}).keys())

    if request.method == "POST":
        emp = {
            "code": random.randint(1000, 9999),
            "name": request.form["name"],
            "username": request.form["username"],
            "password": request.form["password"],
            "role": request.form["role"],
            "exp": int(request.form["exp"]),
            "working_hours": float(request.form["working_hours"]),
            "loan_balance": float(request.form["loan_balance"]),
            "department": request.form.get("department", "General")
        }
        add_employee(data, emp)
        flash("Employee added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("employee_form.html", action="Add", roles=roles, employee={})


# ---------------------- EDIT EMPLOYEE ----------------------
@app.route("/employee/edit/<int:emp_code>", methods=["GET", "POST"])
def edit_employee(emp_code):
    if 'user_role' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    data = load_data()
    emp = find_employee_by_code(data, emp_code)
    roles = list(data.get("roles", {}).keys())

    if not emp:
        flash("Employee not found!", "error")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        emp.update({
            "name": request.form["name"],
            "username": request.form["username"],
            "password": request.form["password"],
            "role": request.form["role"],
            "exp": int(request.form["exp"]),
            "working_hours": float(request.form["working_hours"]),
            "loan_balance": float(request.form["loan_balance"]),
            "department": request.form.get("department", emp.get("department", "General"))
        })
        update_employee(data, emp)
        save_data(data)
        flash("Employee details updated!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("employee_form.html", action="Edit", roles=roles, employee=emp)


# ---------------------- DELETE EMPLOYEE ----------------------
@app.route("/employee/delete/<int:emp_code>")
def delete_employee_route(emp_code):
    if 'user_role' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    data = load_data()
    delete_employee(data, emp_code)
    flash("Employee deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))



# ---------------------- STATIC PDF DOWNLOAD (placeholder) ----------------------
@app.route('/download/<path:filename>')
def download_payslip(filename):
    return send_from_directory("static/payslips", filename, as_attachment=True)


# ---------------------- ERROR HANDLERS ----------------------
@app.errorhandler(404)
def not_found(e):
    return "<h1>404 - Page Not Found</h1>", 404

@app.errorhandler(500)
def server_error(e):
    return "<h1>500 - Server Error</h1>", 500

# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.run(debug=True)
