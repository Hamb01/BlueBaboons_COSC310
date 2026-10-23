from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.error_schema import error_responses
from app.schemas.user_schema import CustomerRegister, CustomerResponse, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

# Owner: Person A (customers + auth)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer account",
    responses=error_responses(409, 422),
)
def register(payload: CustomerRegister, service: AuthService = Depends(get_auth_service)) -> CustomerResponse:
    """Create an active customer account. 409 if the email is already registered."""
    return service.register_customer(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in and receive a bearer token",
    responses=error_responses(401, 403, 422),
)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Exchange email + password for a bearer token. 401 for bad credentials, 403 if deactivated."""
    return service.login(payload)
