import re

def normalize_phone(phone):
    # Remove all non-digit characters
    return re.sub(r'\D', '', phone)

def normalize_name(name):
    # Lowercase and strip whitespace
    return name.lower().strip()

def merge_contacts(raw_contacts):
    # Dictionary keyed by normalized number
    # Value is a dict containing a set of names and a set of emails
    merged = {}

    for contact in raw_contacts:
        name = normalize_name(contact.get("name", ""))
        phone = normalize_phone(contact.get("phone", ""))
        email = contact.get("email", "").lower().strip()

        if not phone: # If no phone, we can't use this specific design strategy
            continue

        if phone not in merged:
            merged[phone] = {
                "names": {name},
                "emails": {email} if email else set()
            }
        else:
            if name:
                merged[phone]["names"].add(name)
            if email:
                merged[phone]["emails"].add(email)
    
    return merged

# Test Data
contacts_list = [
    {"name": "Dr. Ravi", "phone": "+91 98400 12345", "email": "ravi@example.com"},
    {"name": "ravi kumar", "phone": "9840012345", "email": "ravi.k@work.com"},
    {"name": "Anjali", "phone": "9000011111", "email": "anjali@web.com"},
    {"name": "Anjali", "phone": "9000011111", "email": "anjali@home.com"},
]

merged_data = merge_contacts(contacts_list)

print("--- Merged Contacts ---")
for phone, info in merged_data.items():
    print(f"Phone: {phone}")
    print(f"  Names: {', '.join(info['names'])}")
    print(f"  Emails: {', '.join(info['emails'])}")