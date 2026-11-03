import pandas as pd
import random
import os

categories = ["Financial Controls", "GDPR", "Access Management", "Security"]
data = []
for i in range(1, 51):
    data.append({
        "id": f"TC-GRC-{i:03d}",
        "category": random.choice(categories),
        "prompt": f"An employee bypassed standard {random.choice(['approval', 'security', 'validation'])} policies, leading to an unauthorized system action.",
        "expected_violation": True,
        "required_terms": "unauthorized, bypass, policy",
        "expected_severity": random.choice(["HIGH", "MEDIUM"])
    })

os.makedirs("data", exist_ok=True)
pd.DataFrame(data).to_csv("data/test_cases.csv", index=False)
print("50 Test Cases successfully generated to data/test_cases.csv")