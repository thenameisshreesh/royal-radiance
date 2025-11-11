import requests

# ✅ Use the root Supabase project URL (not db.)
SUPABASE_URL = "https://cvnuwppsgrhzvmlfxxzb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2bnV3cHBzZ3JoenZtbGZ4eHpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3Nzg3NjEsImV4cCI6MjA3ODM1NDc2MX0.7IhHKZdeIOLUScF4ui2xhSSxlok1FZVdQoUOtXAcaZA"
TABLE_NAME = "users"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

name = input("Enter Name: ")
email = input("Enter Email: ")
password = input("Enter Password: ")

data = {"name": name, "email": email, "password": password}

# ✅ REST endpoint (no /db/)
response = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}", json=data, headers=headers)

if response.status_code in [200, 201]:
    print(f"✅ User '{name}' added successfully!")
else:
    print(f"❌ Error: {response.status_code} {response.text}")
