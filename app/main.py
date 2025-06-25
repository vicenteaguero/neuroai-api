from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware


from app.auth import create_user, authenticate_user, create_access_token,users_db,SECRET_KEY,ALGORITHM
from app.mri import save_user_file, process_and_save_modalities
from jose import JWTError, jwt
from pydantic import BaseModel

app  = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupModel(BaseModel):
    username:str
    surname:str
    password:str

@app.post("/signup")
def signup(user:SignupModel):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    create_user(user.username,user.password,user.surname)
    return {"message":"User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub":user["username"]})
    return {"access_token":access_token,"token_type":"bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid user")
        return users_db[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
@app.post('/upload-mri')
def upload_mri(file:UploadFile = File(...),user:dict = Depends(get_current_user)):
    file_path, folder = save_user_file(user["username"],user["surname"],file)
    try:
        images  = process_and_save_modalities(file_path,folder)
        return JSONResponse(content={'message':"Success",**images})
    except Exception as e:
        return JSONResponse(status_code = 404, content={"error":str(e)})
    
            
@app.post("/token")
def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
            