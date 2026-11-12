from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import functions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#E1
@app.post("/packages")
def register_package( name, destination, weight,token=Header):
    username=functions.verify_token(token=token)
    if not username:
            raise HTTPException(status_code=401,detail="invalid")
    return functions.register_package(name=name, destination=destination, weight=weight)

#E2
@app.get("/packages/{package_id}")
def get_package_details(package_id,token=Header):
    username=functions.verify_token(token=token)
    if not username:
            raise HTTPException(status_code=401,detail="invalid")
    return functions.get_package_by_id(package_id)

#E3
@app.patch("/packages/{package_id}")
def update_package_details(package_id, name, destination, weight,token=Header):
    username=functions.verify_token(token=token)
    if not username:
            raise HTTPException(status_code=401,detail="invalid")
    return functions.update_package_details(package_id=package_id, name=name, destination=destination, weight=weight)

#E4
@app.delete("/packages/{package_id}")
def delete_package(package_id,token=Header):
    username=functions.verify_token(token=token)
    if not username:
            raise HTTPException(status_code=401,detail="invalid")
    return functions.delete_package(package_id=package_id)

#E5
@app.get("/packages")    
def search_package(destination, status, arrival_date,token=Header(None)):
    username=functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401,detail="invalid")
    return functions.search_package(destination=destination, status=status, arrival_date=arrival_date)

@app.post("/login")
def login(username: str, password: str):
    
    token =functions.verify_login(username=username,password=password)
    if token is None:
        raise HTTPException(status_code=401,detail="invalid")
    return token

@app.post("/refresh")
def refresh(refresh_token = Header(None)):
    functions.verify_token(token = refresh_token, token_type = "refresh")
    username=functions.verify_token(token=refresh_token,token_type="refresh")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or Expired refresh token")

    access_token =  function.create_token (username ="username", token_type = "access")
    return {"access_token": access_token}
          
