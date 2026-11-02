from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.dependencies import get_db
from app.models.auth_identity import AuthIdentity
from app.models.user import User
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserResponse



@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    email = str(payload.email).strip().lower()

    existing_identity = db.scalar(
        select(AuthIdentity.id).where(
            AuthIdentity.provider == "EMAIL",
            AuthIdentity.subject == email,
        )
    )

    if existing_identity is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User()
    identity = AuthIdentity(
        user=user,
        provider="EMAIL",
        subject=email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.add(identity)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        if constraint_name == "uq_auth_identities_provider_subject":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            ) from exc

        raise

    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        email=email,
        created_at=user.created_at,
    )
    
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    email = str(payload.email).strip().lower()

    identity = db.scalar(
        select(AuthIdentity).where(
            AuthIdentity.provider == "EMAIL",
            AuthIdentity.subject == email,
        )
    )

    if (
        identity is None
        or identity.password_hash is None
        or not verify_password(payload.password, identity.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_in = create_access_token(
        subject=str(identity.user_id),
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )
    

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    email = db.scalar(
        select(AuthIdentity.subject).where(
            AuthIdentity.user_id == current_user.id,
            AuthIdentity.provider == "EMAIL",
        )
    )

    return CurrentUserResponse(
        id=current_user.id,
        email=email,
        created_at=current_user.created_at,
    )