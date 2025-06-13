from datetime import datetime, timedelta
from jose import jwt

from app.core.config import settings

def create_mini_app_access_token(transaction_hash: str) -> str:
    """
    Creates a short-lived JWT for the Mini App to use.
    The token is specific to one transaction hash.
    """
    expire = datetime.utcnow() + timedelta(hours=128)
    to_encode = {
        "exp": expire,
        "sub": "mini_app_user",
        "txn_hash": transaction_hash 
    }
    encoded_jwt = jwt.encode(to_encode, key=settings.APP_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
    
    
    return encoded_jwt