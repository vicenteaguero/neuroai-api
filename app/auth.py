from passlib.context import CryptContext
from jose import JWSError, jwt 
from datetime import datetime, timedelta


pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users_db = {}

def hash_password(password: str):
    return pwd_content.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_content.verify(plain_password, hashed_password)

def create_user(username:str,password:str,surname:str):
    users_db[username] = {
        "username":username,
        "surname":surname,
        "password":hash_password(password)
    }

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(data: dict,expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

