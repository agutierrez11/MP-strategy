import os
import requests, json

token = os.getenv("APIFY_API_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"}

# Check user profile & limits
res = requests.get("https://api.apify.com/v2/users/me", headers=headers)
print("User info status:", res.status_code)
if res.status_code == 200:
    data = res.json().get("data", {})
    print("Username:", data.get("username"))
    print("Email:", data.get("email"))
    limits = data.get("limits", {})
    print("Limits:", json.dumps(limits, indent=2))
    usage = data.get("usage", {})
    print("Usage:", json.dumps(usage, indent=2))
    plan = data.get("plan", {})
    print("Plan:", plan)
else:
    print("Error:", res.text)
