import re
import json

def parse_raw_data(raw_text):
    # Split the text by numbered entries. This is a more robust way to separate entries.
    entries_text = re.split(r'\n\d+\.\s+', raw_text)

    data = []
    current_category = "General"

    # Regex for category headers
    category_pattern = re.compile(r'^[A-Z\s]+$')

    for entry_text in entries_text:
        if not entry_text.strip():
            continue

        lines = entry_text.strip().split('\n')
        first_line = lines[0].strip()

        # Check for category headers within the entry text
        # This is not ideal, but the data format is inconsistent
        possible_category = first_line if len(lines) == 1 else None
        if possible_category and category_pattern.match(possible_category) and "S. No" not in possible_category and "Phone" not in possible_category:
            current_category = possible_category.title()
            continue

        process_entry(lines, current_category, data)

    return data

def process_entry(entry_lines, category, data):
    full_entry_text = ' '.join([line.strip() for line in entry_lines])

    # Regex patterns for contact details
    phone_pattern = r'(\b\d{2,4}[-\s]?\d{6,}\b|\b\d{10}\b)'
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    website_pattern = r'www\.[\w\.-]+'

    phone_numbers = re.findall(phone_pattern, full_entry_text)
    emails = re.findall(email_pattern, full_entry_text)
    websites = re.findall(website_pattern, full_entry_text)

    text_for_parsing = full_entry_text
    for p in phone_numbers:
        text_for_parsing = text_for_parsing.replace(p, '')
    for e in emails:
        text_for_parsing = text_for_parsing.replace(e, '')
    for w in websites:
        text_for_parsing = text_for_parsing.replace(w, '')

    # Cleanup
    text_for_parsing = re.sub(r'Ph\s*:\s*', '', text_for_parsing, flags=re.IGNORECASE)
    text_for_parsing = re.sub(r'Fax\s*:\s*', '', text_for_parsing, flags=re.IGNORECASE)
    text_for_parsing = re.sub(r'Mob\s*:\s*', '', text_for_parsing, flags=re.IGNORECASE)
    text_for_parsing = re.sub(r'e-mail\s*:\s*', '', text_for_parsing, flags=re.IGNORECASE)
    text_for_parsing = re.sub(r'\s{2,}', ' ', text_for_parsing).strip()

    # Heuristics for name and address
    parts = text_for_parsing.split(',')
    name = parts[0]
    address = ','.join(parts[1:])

    # Further cleanup and structuring
    name = name.strip()
    address = address.strip()

    # Attempt to handle cases where the category is the last line of the previous entry
    category_match = re.search(r'([A-Z\s]{5,})$', address)
    if category_match:
        possible_category = category_match.group(1).strip()
        if len(possible_category.split()) > 1: # Basic check if it's a plausible category name
            # This is a heuristic and might misclassify
            # address = address.replace(possible_category, '').strip()
            pass # For now, let's not alter the address, just observe

    data.append({
        "category": category,
        "name": name,
        "address": address,
        "phone": list(set(phone_numbers)),
        "email": list(set(emails)),
        "website": list(set(websites))
    })

if __name__ == '__main__':
    with open('raw.txt', 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Manually add a newline before the first entry to help the split regex
    raw_text = "\n1. " + raw_text.split("1. ", 1)[1]

    parsed_data = parse_raw_data(raw_text)

    with open('data.json', 'w') as f:
        json.dump(parsed_data, f, indent=4)

    print("Parsing complete. Data saved to data.json")
