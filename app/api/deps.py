from app.db.session import get_db  # noqa: F401

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False) 

async def get_api_key(api_key: str = Depends(api_key_header_scheme)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-API-KEY header missing")
    if api_key != settings.IPHONE_SHORTCUT_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return api_key

mini_app_auth_scheme = APIKeyHeader(name="Authorization", auto_error=False)


class TokenData(BaseModel):
    txn_hash: str

async def get_current_transaction_from_token(
    authorization: str = Depends(mini_app_auth_scheme) # Use the new scheme
) -> TokenData:
    """
    Dependency that decodes and validates a Mini App JWT from the Authorization header.
    Returns the payload containing the transaction hash.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization or not authorization.startswith("Bearer"):
        raise credentials_exception
        
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, key=settings.APP_SECRET_KEY, algorithms=settings.TOKEN_ALGORITHM)
        txn_hash: str = payload.get("txn_hash")
        if txn_hash is None:
            raise credentials_exception
        token_data = TokenData(txn_hash=txn_hash)
    except JWTError as e:
        raise credentials_exception
    
    return token_data

async def get_transaction_hash_from_token(
    token_data: TokenData = Depends(get_current_transaction_from_token)
) -> str:
    return token_data.txn_hash