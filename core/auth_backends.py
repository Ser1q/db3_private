from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password, make_password

from .models import AppUser


class AppUserBackend(BaseBackend):
    """
    Authenticate against the existing AppUser table while keeping Django's auth user in sync.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            app_user = AppUser.objects.get(email=username)
        except AppUser.DoesNotExist:
            return None

        stored_pw = app_user.password or ""
        is_hashed = stored_pw.startswith(("pbkdf2_", "argon2", "bcrypt", "scrypt"))

        if is_hashed:
            valid = check_password(password, stored_pw)
        else:
            valid = stored_pw == password

        if not valid:
            return None

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=app_user.email,
            defaults={
                "email": app_user.email,
                "first_name": app_user.given_name,
                "last_name": app_user.surname,
            },
        )

        # Ensure auth user mirrors AppUser
        needs_pw_update = not check_password(password, user.password)
        if created or needs_pw_update:
            user.password = make_password(password)
            user.email = app_user.email
            user.first_name = app_user.given_name
            user.last_name = app_user.surname
            user.save()

        # Harden AppUser password to hashed form if it was plain
        if not is_hashed:
            app_user.password = user.password
            app_user.save(update_fields=["password"])

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
