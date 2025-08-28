import phonenumbers

def normalize_phone(raw_number: str) -> str:
    try:
        parsed = phonenumbers.parse(raw_number, "IN")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return raw_number.strip()
