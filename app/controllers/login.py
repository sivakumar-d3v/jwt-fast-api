from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.data.database import get_db
from app.data import schemas, models
from app.controllers.auth import generate_jwt_access_token, authenticate_user
from app.controllers.auth import decode_auth_token, PasswordHashing
router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
async def login(request: schemas.Login, db:Session= Depends(get_db)):
    user = authenticate_user(db, username = request.email, password= request.password)

    access_token = generate_jwt_access_token(name=user.name, email=user.email)

    # refresh_token = generate_jwt_access_token(name=user.name, email=user.email) 

    return {"access_token":access_token, "token_type":"bearer"}

@router.post("/users/me/", response_model=schemas.UserOut)
async def read_users_token(request: schemas.Token,db:Session=Depends(get_db)):
    user_info = decode_auth_token(request.access_token)
    return user_info

@router.post("/sign-up", status_code =status.HTTP_201_CREATED, summary="Sign up")
async def create_user(request: schemas.User, db: Session = Depends(get_db), password_hashing: PasswordHashing = Depends(PasswordHashing)):
    try:
        check_user_email = db.query(models.User).filter(models.User.email == request.email).first() is not None
        if check_user_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email is already exist")
        
        hashed_password = password_hashing.hash_password(password=request.password)
        new_user = models.User(name = request.name, email = request.email, password = hashed_password, added_on = datetime.now())
        db.add(new_user)
        db.commit()
        return "Successfully created a user"
    except Exception as e:
        db.rollback()
        print("Error in creating user", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")