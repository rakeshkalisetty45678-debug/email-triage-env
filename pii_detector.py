tee pii_detector.py > /dev/null << 'MYEOF'
import re
import requests
import base64

OM_HOST = "http://localhost:8585"

def get_token():
    password = base64.b64encode("admin".encode()).decode()
    response = requests.post(
        f"{OM_HOST}/api/v1/users/login",
        json={"email": "admin@open-metadata.org", "password": password}
    )
    return response.json()["accessToken"]

PII_PATTERNS = {
    "EMAIL": r"email|e_mail|user_mail",
    "PHONE": r"phone|mobile|contact_no|ph_no|cell",
    "NAME": r"first_name|last_name|full_name|customer_name",
    "ADDRESS": r"street|pincode|zipcode",
    "AADHAR": r"aadhar|aadhaar",
    "PAN": r"pan_no|pan_number",
    "DOB": r"dob|date_of_birth|birthdate",
    "GENDER": r"gender|sex",
}

def detect_pii(column_name):
    column_lower = column_name.lower()
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, column_lower):
            return pii_type
    return None

def get_all_tables(headers):
    url = f"{OM_HOST}/api/v1/tables?limit=200"
    response = requests.get(url, headers=headers)
    return response.json().get("data", [])

def scan_tables():
    print("Getting token...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("Token received!")
    tables = get_all_tables(headers)
    print(f"Found {len(tables)} tables!")
    pii_findings = []
    for table in tables:
        table_name = table.get("name")
        columns = table.get("columns", [])
        for col in columns:
            col_name = col.get("name", "")
            pii_type = detect_pii(col_name)
            if pii_type:
                pii_findings.append({"table": table_name, "column": col_name, "pii_type": pii_type})
                print(f"PII Found: {table_name}.{col_name} -> {pii_type}")
    print(f"Total PII columns found: {len(pii_findings)}")
    return pii_findings

if __name__ == "__main__":
    scan_tables()
MYEOF