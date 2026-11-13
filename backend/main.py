from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date

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
def register_package( name, destination, weight,  token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.register_package(name=name, destination=destination, weight=weight)

#E2
@app.get("/packages/{package_id}")
def get_package_details(package_id,  token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.get_package_by_id(package_id)

#E3
@app.patch("/packages/{package_id}")
def update_package_details(package_id, name, destination, weight, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.update_package_details(package_id=package_id, name=name, destination=destination, weight=weight)

#E4
@app.delete("/packages/{package_id}")
def delete_package(package_id,  token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.delete_package(package_id=package_id)

#E5
@app.get("/packages")    
def search_package(destination= None, status= None, arrival_date= None,  token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.search_package(destination=destination, status=status, arrival_date=arrival_date)

#E6
@app.get("/dispatch-batches")
def view_dispatchBatches(destination, vehicle_number, dispatch_status,  token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.view_dispatchBatches(destination=destination, vehicle_number=vehicle_number, dispatch_status=dispatch_status)

#E7
@app.get("/warehouse/summary")
def warehouse_summary( token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.get_warehouse_summary()

#E8 
@app.post("/dispatch-batches")
def add_dispatch(destination, vehicle_number, dispatch_date, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    return functions.create_dispatchBatches(destination=destination, vehicle_number=vehicle_number, dispatch_date=dispatch_date)


@app.post("/login")
def login(username= Body(), password= Body()):
    token =  functions.verify_login(username = username, password=password)
    if not token  :
        raise HTTPException(status_code = 401, detail="Invalid credentials")
    return token

@app.post("/refresh")
def refresh(refresh_token = Header(None)):
   username =  functions.verify_token(token=refresh_token , token_type= "refresh")
   if not username:
       raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
   
   access_token = functions.create_token(username=username, token_type= "access")
   return {"access_token" : access_token}

@app.post("/register")
def register_user(user_name= Body(), password = Body()):
    if functions.register_user(user_name=user_name, password=password):
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")