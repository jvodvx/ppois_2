def to_int(value: str):
    value = value.strip()
    if not value:
        return None

    try:
        return int(value)
    except ValueError as error:
        raise ValueError("Введите целое число") from error


def to_float(value: str):
    value = value.strip().replace(",", ".")
    if not value:
        return None

    try:
        return float(value)
    except ValueError as error:
        raise ValueError("Введите число") from error


def empty_to_none(value: str):
    value = value.strip()
    return value if value else None
