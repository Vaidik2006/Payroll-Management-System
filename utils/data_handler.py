# utils/data_handler.py
"""
Simple JSON data handler for employees.json
- load_data(): returns full JSON as dict
- save_data(data): writes dict back to file
- helpers: find employee by code or username
"""

import json
import os
from typing import Optional

DATA_PATH = os.path.join("data", "employees.json")

def ensure_data_path():
    folder = os.path.dirname(DATA_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        # create minimal skeleton if missing
        skeleton = {
            "roles": {},
            "employees": [],
            "payroll_history": [],
            "logins": { "admin": {"username":"admin", "password":"password"} }
        }
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(skeleton, f, indent=2)

def load_data() -> dict:
    ensure_data_path()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: dict):
    ensure_data_path()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def find_employee_by_code(data: dict, code: int) -> Optional[dict]:
    for e in data.get("employees", []):
        if int(e.get("code", -1)) == int(code):
            return e
    return None

def find_employee_by_username(data: dict, username: str) -> Optional[dict]:
    for e in data.get("employees", []):
        if e.get("username") == username:
            return e
    return None

def update_employee(data: dict, updated_emp: dict):
    """Replace the employee entry (matched by code) with updated_emp and persist in-memory dict."""
    arr = data.get("employees", [])
    for i, e in enumerate(arr):
        if int(e.get("code", -1)) == int(updated_emp.get("code", -1)):
            arr[i] = updated_emp
            return True
    # not found -> append
    arr.append(updated_emp)
    return True

def add_employee(data: dict, new_emp: dict):
    """Add a new employee to the data and persist."""
    employees = data.get("employees", [])
    employees.append(new_emp)
    data["employees"] = employees
    save_data(data)

def delete_employee(data: dict, emp_code: int):
    """Delete an employee by their code."""
    employees = [e for e in data.get("employees", []) if int(e.get("code", -1)) != int(emp_code)]
    data["employees"] = employees
    save_data(data)
