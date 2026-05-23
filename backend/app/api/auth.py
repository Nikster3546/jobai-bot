from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import verify_telegram_init_data, create_access_token
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str  # строка initData от TWA


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/tg-verify", response_model=TokenResponse)
async def telegram_verify(
    body: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    user_data = verify_telegram_init_data(body.init_data)
    if not user_data:
        raise HTTPException(status_code=401, detail="Невалидная подпись Telegram")

    user_id = int(user_data["id"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=user_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        db.add(user)
        await db.flush()

    token = create_access_token(user_id)
    return TokenResponse(access_token=token)