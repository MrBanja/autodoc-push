from pydantic import BaseModel


class BasicPush(BaseModel):
    telegram_user_id: int
    message: str
