import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.data import models
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer


SECRET_KEY = "jwt-fast-api-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()


class PasswordHashing:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def hash_password(self,password):
        return self.pwd_context.hash(password)

    def verify_password(self,plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)


def generate_jwt_access_token(name, email):
    payload= {
        "name": name,
        "email": email,
        "disabled": False,
        "exp" : datetime.utcnow()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(
        payload,
        key = SECRET_KEY,
        algorithm = ALGORITHM
    )
    return access_token

def get_user(db, username:str):
    user = db.query(models.User).filter(models.User.email == username).first()
    return user
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found.")

    hasing_password = PasswordHashing()
    if not hasing_password.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    return user

def get_access_token(request):
    if "Bearer" in request.scheme:
        return request.credentials
    raise None


def jwt_auth_wrapper(request: HTTPBearer = Security(security)):
    try:
        print("Request Headers:", request)
        token = get_access_token(request)
        if token:
            return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def decode_auth_token(token):
    try:
        return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


