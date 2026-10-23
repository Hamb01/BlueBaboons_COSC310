from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CurrentUser, CustomerRegister, CustomerResponse, LoginRequest, TokenResponse


class AuthService:
    """Service layer for registration, sign-in, and identifying the caller of a request.

    Owner: Person A (customers + auth).
    TODO (design first): which authentication mechanism? (session token, JWT, ...)
          Can you build it without adding a dependency? How are passwords stored safely?
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_customer(self, payload: CustomerRegister) -> CustomerResponse:
        # TODO: which business rules apply when registering?
        raise NotImplementedError("AuthService.register_customer")

    def login(self, payload: LoginRequest) -> TokenResponse:
        # TODO: should "wrong email" and "wrong password" give the same error? Why?
        # TODO: can a deactivated account sign in?
        raise NotImplementedError("AuthService.login")

    def get_current_user(self, token: str) -> CurrentUser:
        # TODO: called on every protected request — what makes a token invalid?
        raise NotImplementedError("AuthService.get_current_user")
