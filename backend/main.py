from fastapi import FastAPI, HTTPException
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
def register_package( name, destination, weight):
    return functions.register_package(name=name, destination=destination, weight=weight)

#E2
@app.get("/packages/{package_id}")
def get_package_details(package_id):
    return functions.get_package_by_id(package_id)

#E3
@app.patch("/packages/{package_id}")
def update_package_details(package_id, name, destination, weight):
    return functions.update_package_details(package_id=package_id, name=name, destination=destination, weight=weight)

#E4
@app.delete("/packages/{package_id}")
def delete_package(package_id):
    return functions.delete_package(package_id=package_id)

