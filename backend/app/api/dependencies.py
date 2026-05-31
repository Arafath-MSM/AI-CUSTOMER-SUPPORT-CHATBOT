from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_admin_token(
    x_admin_token: str | None = Header(default=None),
) -> None:
    if not settings.verify_admin_token(x_admin_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid admin token is required.",
        )
