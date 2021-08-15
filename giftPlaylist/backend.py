from django.contrib.auth.backends import ModelBackend
from giftPlaylist.models import User

# Log in to Django without providing a password.
class PasswordlessAuthBackend(ModelBackend):
    def authenticate(self, username=None):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 
