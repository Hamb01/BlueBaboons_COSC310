from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CurrentUser, CustomerRegister, CustomerResponse, LoginRequest, TokenResponse


class AuthService:
    """Service layer for registration, sign-in, and resolving bearer tokens.

    Owner: Person A (customers + auth).
    Suggested approach (stdlib only, no new dependencies):
      - hash passwords with hashlib.pbkdf2_hmac + a random salt (secrets.token_hex)
      - issue tokens with secrets.token_urlsafe and store them via UserRepository.save_session
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_customer(self, payload: CustomerRegister) -> CustomerResponse:
        """Create an active customer account.

        Raises EmailAlreadyRegisteredError if the email is taken.
        """
        raise NotImplementedError("AuthService.register_customer")

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Check the email/password and issue a new bearer token.

        Raises AuthenticationError for a wrong email or password (same message for both),
        and InactiveAccountError for a deactivated account.
        """
        raise NotImplementedError("AuthService.login")

    def get_current_user(self, token: str) -> CurrentUser:
        """Resolve a bearer token to the user it belongs to.

        Called by the get_current_user dependency on every protected request.
        Raises AuthenticationError for an unknown token and InactiveAccountError
        for a deactivated account.
        """
        raise NotImplementedError("AuthService.get_current_user")
