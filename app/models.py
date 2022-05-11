from pydantic import BaseModel


class BasicPush(BaseModel):
    telegram_user_id: int
    message: str
    is_cell_message: bool = False


class CellMessage(BasicPush):
    cell_id: int
    is_sending: bool
