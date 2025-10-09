import csv
data = []
with open("city_data (1).csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        data.append(row)


def validate_id (id):
    try:
        return int(id)
    except (ValueError, TypeError):
        return None

def validate_age(age):
        try:
         return int(age)
        except (ValueError, TypeError):
            return None

import re
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return email if email and re.match(pattern, email) else None
def validate_entry(entry):
    id = validate_id(entry.get("ID"))
    age = validate_age(entry.get("Age"))
    email = validate_email(entry.get("Email"))
    name = entry.get("Name")


    if not (id and age and email and name):
        return None  # Invalid entry
    return {"ID": id, "Name": name, "Age": age, "Email": email}

valid_entries = []
invalid_entries = []

for entry in data:
    validated = validate_entry(entry)
    if validated:
        valid_entries.append(validated)
    else:
        invalid_entries.append(entry)

print("\n Valid Entries:")
for v in valid_entries:
    print(v)   # Show each valid entry on screen

print("\n Invalid Entries:")
for inv in invalid_entries:
     print(inv)
if valid_entries:
    avg_age = sum(u["Age"] for u in valid_entries) / len(valid_entries)
    print(" Average Age of Valid Entries:", avg_age)
else:
    print("No valid entries found.") 
