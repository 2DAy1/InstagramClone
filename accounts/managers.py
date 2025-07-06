from django.contrib.auth.base_user import BaseUserManager
from .utils import validate_required_fields

class UserManager(BaseUserManager):
    def create_user(
        self,
        username: str,
        full_name: str | None = None,
        password: str | None = None,
        **extra_fields
    ):
        is_super = extra_fields.get("is_superuser", False)

        if not is_super:
            validate_required_fields(username=username, full_name=full_name)
            email = extra_fields.get("email")
            phone = extra_fields.get("phone_number")
            if not email and not phone:
                raise ValueError("You must provide at least an email or phone number.")

        if extra_fields.get("email"):
            extra_fields["email"] = self.normalize_email(extra_fields["email"])

        user = self.model(
            username=username,
            full_name=full_name or "",
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        password: str | None = None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            username=username,
            full_name="",
            password=password,
            **extra_fields
        )
