from django.contrib.auth.backends import ModelBackend
from users.models import MainUser
from django.core.exceptions import ObjectDoesNotExist


class CustomBackend(ModelBackend):
    """
    Custom Authentication Class
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on the username and password.
        :param request: The request object.
        :param username: The username of the user.
        :param password: The password of the user.
        """
        if username is None:
            return None
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = MainUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
