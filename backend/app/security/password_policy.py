import re


def validate_password(password, *, min_len=8, max_len=128):
    errors = []

    if password is None:
        password = ""

    if len(password) < min_len:
        errors.append("passwordTooShort")

    if len(password) > max_len:
        errors.append("passwordTooLong")

    if not re.search(r"[A-Z]", password):
        errors.append("passwordWithoutUpper")

    if not re.search(r"\d", password):
        errors.append("passwordWithoutDigits")

    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("passwordWithoutSpecial")

    return errors
