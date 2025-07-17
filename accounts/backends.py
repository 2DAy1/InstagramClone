from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .utils import is_valid_email, is_valid_phone_number

User = get_user_model()


class EmailPhoneUsernameBackend(ModelBackend):
    """
    Authentication backend: allows login via email, phone number or username.
    """

    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs) -> User | None:
        """
        Authenticate a user based on email, phone number or username.
        """
        if not username or not password:
            return None

        user = self.get_user_by_identifier(username)
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user_by_identifier(self, identifier: str) -> User | None:
        """
        Return the user based on one of three options:
        - Email (validated via validate_email)
        - Phone number (validated via phonenumbers)
        - Username (if not email and not phone)
        """
        try:
            if is_valid_email(identifier):
                return User.objects.get(email__iexact=identifier)
            elif is_valid_phone_number(identifier):
                return User.objects.get(phone_number=identifier)
            else:
                return User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            return None
