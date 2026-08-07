
from auth0.v3.management import Auth0
from auth0.v3.authentication import GetToken
from src.api.services.user_service import create_user_with_confirmation

class AuthService:
    def __init__(self, auth0_domain, auth0_client_id, auth0_client_secret):
        self.auth0_domain = auth0_domain
        self.auth0_client_id = auth0_client_id
        self.auth0_client_secret = auth0_client_secret
        self.auth0 = Auth0(auth0_domain, self._get_management_token())

    def _get_management_token(self):
        get_token = GetToken(self.auth0_domain)
        token = get_token.client_credentials(
            self.auth0_client_id,
            self.auth0_client_secret,
            'https://{}/api/v2/'.format(self.auth0_domain)
        )
        return token['access_token']

    def signup_user(self, email, password):
        # Create user in local DB
        user = create_user_with_confirmation(email, password)

        # Provision user in Auth0
        self.auth0.users.create({
            'email': email,
            'password': password,
            'connection': 'Username-Password-Authentication'
        })

        return user

    def login_user(self, email, password):
        # Authenticate with Auth0
        try:
            auth0_user = self.auth0.authenticate(
                username=email,
                password=password,
                realm='Username-Password-Authentication',
                audience='https://{}/api/v2/'.format(self.auth0_domain),
                client_id=self.auth0_client_id,
                client_secret=self.auth0_client_secret
            )
            return auth0_user
        except Exception as e:
            raise Exception("Login failed: {}".format(str(e)))

# Note: Ensure to handle exceptions and edge cases in production code.
