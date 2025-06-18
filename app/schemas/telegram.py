from pydantic import BaseModel
from typing import Optional

# These models represent the nested structure of a Telegram callback query update.
# Currently only required fileds are defined.

class Chat(BaseModel):
    id: int

class Message(BaseModel):
    message_id: int
    chat: Chat

class CallbackQuery(BaseModel):
    id: str
    data: Optional[str] = None
    message: Optional[Message] = None

class TelegramUpdate(BaseModel):
    update_id: int
    callback_query: Optional[CallbackQuery] = None