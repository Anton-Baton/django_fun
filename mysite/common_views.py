from registration.backends.simple.views import RegistrationView


class CustomRegistrationView(RegistrationView):

    def get_success_url(self, user=None):
        return '/rango/'



