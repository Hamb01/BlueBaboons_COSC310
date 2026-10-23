from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.user_schema import CustomerRegister, CustomerResponse, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

# Owner: Person A (customers + auth)
# TODO: these paths are a PROPOSAL — agree on them in the contracts PR review.
# TODO: document each route's error responses in OpenAPI once you know them (see error_schema.py).
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer account",
)
def register(payload: CustomerRegister, service: AuthService = Depends(get_auth_service)) -> CustomerResponse:
    return service.register_customer(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in",
)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(payload)
