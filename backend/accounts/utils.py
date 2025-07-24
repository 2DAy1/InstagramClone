import phonenumbers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def is_valid_email(value: str) -> bool:
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def is_valid_phone_number(phone: str) -> bool:
    try:
        number = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(number)
    except phonenumbers.NumberParseException:
        return False


def validate_required_fields(**fields):
    for field_name, value in fields.items():
        if not value:
            raise ValueError(f"{field_name} is required")
