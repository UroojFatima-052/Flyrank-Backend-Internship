import os
from fastapi import FastAPI, HTTPException
from supabase import create_client
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# root route
@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}


# signup request 
class SignupInput(BaseModel):
     email : str
     password : str

@app.post("/auth/signup", status_code=201)
def sign_up(signUp_data : SignupInput):
    if not signUp_data.email  or  not signUp_data.password:
            return JSONResponse(status_code=400, content={"error": "Email or Password can't be empty."})
    try:
        response = supabase.auth.sign_up({"email": signUp_data.email, "password": signUp_data.password})
        return response.user
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# login request
class LoginInput(BaseModel):
     email : str
     password : str

@app.post("/auth/login", status_code=200)
def login(login_data : LoginInput):
    if not login_data.email  or  not login_data.password:
                return JSONResponse(status_code=400, content={"error": "Email or Password can't be empty."})
    try:
        response = supabase.auth.sign_in_with_password({"email": login_data.email, "password": login_data.password})
        return {
            "access_token" : response.session.access_token,
            "refresh_token" : response.session.refresh_token,
            "user" : response.user
        }
    except Exception as e:
        return JSONResponse(status_code=401, content={"error" : "Invalid login credentials"})