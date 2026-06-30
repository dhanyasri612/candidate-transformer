import re

def normalize_phone(phone: str) -> str:
    if not phone:
        return ""

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        digits = "91" + digits

    return "+" + digits