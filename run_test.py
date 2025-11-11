# run_test.py
# Quick script to test loading JSON, calculating pay for one employee,
# updating and saving back to the JSON store.

from utils.data_handler import load_data, save_data, find_employee_by_code, update_employee
from utils.salary_calculator import calculate_for_employee_record
import pprint

def main():
    data = load_data()
    # pick an existing employee code from your employees.json
    emp_code = 101
    emp = find_employee_by_code(data, emp_code)
    if not emp:
        print("Employee not found:", emp_code)
        return
    print("Before calculation (employee snapshot):")
    pprint.pprint(emp)

    breakdown, updated_emp = calculate_for_employee_record(emp, roles_dict=data.get("roles", {}))
    print("\nCalculated breakdown:")
    pprint.pprint(breakdown)

    update_employee(data, updated_emp)
    save_data(data)
    print("\nEmployee updated and saved back to data/employees.json")

if __name__ == "__main__":
    main()
