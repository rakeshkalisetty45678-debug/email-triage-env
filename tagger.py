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

def get_token_headers():
    token = get_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_all_tables(headers):
    url = f"{OM_HOST}/api/v1/tables?limit=200"
    response = requests.get(url, headers=headers)
    return response.json().get("data", [])

def tag_column(table_data, col_name, pii_type, headers):
    tag_fqn = "PII.Sensitive"
    columns = table_data.get("columns", [])
    for col in columns:
        if col.get("name") == col_name:
            existing_tags = col.get("tags", [])
            new_tag = {
                "tagFQN": tag_fqn,
                "source": "Classification",
                "labelType": "Automated",
                "state": "Confirmed"
            }
            if not any(t.get("tagFQN") == tag_fqn for t in existing_tags):
                existing_tags.append(new_tag)
                col["tags"] = existing_tags
    patch_url = f"{OM_HOST}/api/v1/tables/{table_data.get('id')}"
    patch_response = requests.put(patch_url, json=table_data, headers=headers)
    if patch_response.status_code == 200:
        print(f"✅ Tagged: {col_name} -> PII.Sensitive")
    else:
        print(f"❌ Failed: {col_name} -> {patch_response.status_code}")

def scan_and_tag():
    print("🔑 Getting token...")
    headers = get_token_headers()
    print("📋 Fetching tables...")
    tables = get_all_tables(headers)
    print(f"✅ Found {len(tables)} tables!")
    count = 0
    for table in tables:
        table_fqn = table.get("fullyQualifiedName")
        columns = table.get("columns", [])
        for col in columns:
            col_name = col.get("name", "")
            pii_type = detect_pii(col_name)
            if pii_type:
                print(f"🔴 PII Found: {table_fqn}.{col_name} -> {pii_type}")
                tag_column(table, col_name, pii_type, headers)
                count += 1
    print(f"\n🎯 Total tagged: {count} PII columns!")

if __name__ == "__main__":
    scan_and_tag()