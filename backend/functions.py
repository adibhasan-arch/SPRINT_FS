from sqlalchemy import Integer, String, Column, create_engine, ForeignKey, DateTime, func
from sqlalchemy.orm import Session, declarative_base;
from datetime import timedelta, datetime, timezone,date;
from fastapi import HTTPException
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional

ph = PasswordHasher()

DB_PATH = "warehouse.db"

engine = create_engine(f"sqlite:///{DB_PATH}")

USERNAME = "Adib"
PASSWORD = "12345"
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

Base = declarative_base()

class packages(Base):
    __tablename__="packages"
    package_id = Column(Integer, primary_key=True)
    name = Column(String)
    destination = Column(String)
    weight = Column(Integer)
    arrival_date = Column(DateTime)
    status = Column(String)
    dispatchBatchID = Column(Integer, ForeignKey("DispatchBatch.id"), nullable=True)

class DispatchBatch(Base):
    __tablename__="DispatchBatch"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle_number = Column(Integer)
    dispatch_status = Column(String, default="Pending")
    dispatch_date = Column(DateTime)
    created_at = Column(String)

class Users(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key= True)
    role = Column(String, default = "staff")
    user_name = Column(String)
    password= Column(String)
    
    
    
#------------Pydantic----------------
def clean_text(value):
    if value is None: # PackageUpdate fields can be None
        return value
    value = value.strip()
    if value == "":
        raise ValueError("cannot be blank")
    return value

#E1, E8 and login 
class PackageCreate(BaseModel):
    name: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    weight: int = Field(gt=0)

    @field_validator("name", "destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

class DispatchBatchCreate(BaseModel):
    destination: str = Field(min_length=1)
    vehicle_number: int = Field(gt=0)

    @field_validator("destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

class LoginRequest(BaseModel):
    username: str
    password: str
    
    
#  E3 
class PackageUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    destination: Optional[str] = Field(default=None, min_length=1)
    weight: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def something_to_update(self):
        if self.name is None and self.destination is None and self.weight is None:
            raise ValueError("Nothing to update")
        return self

    @field_validator("name", "destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)
    
    
# E5 and E6 
class PackageSearch(BaseModel):
    destination: Optional[str] = None
    status: Optional[str] = None
    arrival_date: Optional[date] = None 

    @field_validator("status")
    @classmethod
    def valid_status(cls, value):
        if value is not None and value not in ["Registered", "Dispatched"]:
            raise ValueError("Invalid status")
        return value

class DispatchBatchSearch(BaseModel):
    destination: Optional[str] = None
    vehicle_number: Optional[int] = None   
    dispatch_status: Optional[str] = None

    @field_validator("dispatch_status")
    @classmethod
    def valid_dispatch_status(cls, value):
        if value is not None and value not in ["Pending", "Dispatched"]:
            raise ValueError("Invalid dispatch status")
        return value


#  E2, E5 and login
class PackageOut(BaseModel):
    package_id: int
    name: str
    destination: str
    weight: int
    arrival_date: datetime
    status: str


    
    
Base.metadata.create_all(engine)

# E1
def register_package(name, destination, weight):
    session = Session(engine)
    new_package = packages(
        name=name,
        destination=destination,
        weight=weight,
        arrival_date=datetime.now(),
        status="Registered",
    )
    session.add(new_package)
    session.commit()
    response = {
        "package_id": new_package.package_id,
        "name": new_package.name,
        "destination": new_package.destination,
        "weight": new_package.weight,
        "arrival_date": new_package.arrival_date,
        "status": new_package.status,
    }
    session.close()
    return response

# E2 - returns None if not found
def get_package_by_id(package_id):
    session = Session(engine)
    package = session.get(packages, package_id)
    if package is None:
        session.close()
        return None
    response = package
    session.close()
    return response

# E3
def update_package_details(package_id, name=None, destination=None, weight=None):
    session = Session(engine)
    package = session.get(packages, package_id)
    if package is None:
        session.close()
        return None
    if name is not None:
        package.name = name
    if destination is not None:
        package.destination = destination
    if weight is not None:
        package.weight = weight
    session.commit()
    session.close()
    return {"message": "Package updated successfully"}

# E4
def delete_package(package_id):
    session = Session(engine)
    package = session.get(packages, package_id)
    session.delete(package)
    session.commit()
    session.close()
    return {"message": "Package deleted successfully"}

# E5 
def search_package(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    query = session.query(packages)

    if destination is not None:
        query = query.filter(packages.destination == destination)
    if status is not None:
        query = query.filter(packages.status == status)
    if arrival_date is not None:
        query = query.filter(func.date(packages.arrival_date) == arrival_date)

    response = []
    for package in query.all():
        response.append(package)

    session.close()
    return response

# E6 - returns an empty list if nothing matches
def view_dispatchBatches(destination=None, vehicle_number=None, dispatch_status=None):
    session = Session(engine)
    query = session.query(DispatchBatch)

    if destination is not None:
        query = query.filter(DispatchBatch.destination == destination)
    if vehicle_number is not None:
        query = query.filter(DispatchBatch.vehicle_number == vehicle_number)
    if dispatch_status is not None:
        query = query.filter(DispatchBatch.dispatch_status == dispatch_status)

    response = []
    for dispatch_batch in query.all():
        response.append({
            "id": dispatch_batch.id,
            "destination": dispatch_batch.destination,
            "vehicle_number": dispatch_batch.vehicle_number,
            "dispatch_status": dispatch_batch.dispatch_status,
            "dispatch_date": dispatch_batch.dispatch_date,
            "created_at": dispatch_batch.created_at,
        })

    session.close()
    return response

# E7
def get_warehouse_summary():
    session = Session(engine)
    package_list = session.query(packages).all()

    dispatched = 0
    destination_count = {}

    for package in package_list:
        if package.status == "Dispatched":
            dispatched = dispatched + 1
       

        if package.destination in destination_count:
            destination_count[package.destination] = destination_count[package.destination] + 1
        else:
            destination_count[package.destination] = 1

    session.close()
    return {
        "total_packages": len(package_list),
        "dispatched": dispatched,
        "destination_wise_count": destination_count,
    }

# E8
def create_dispatchBatches(destination, vehicle_number):
    session = Session(engine)
    new_dispatch_batch = DispatchBatch(
        destination=destination,
        vehicle_number=vehicle_number,
        dispatch_status="Dispatched",
        dispatch_date=datetime.now(),
        created_at=datetime.now().strftime("%Y-%m-%d"),
    )
    
    session.add(new_dispatch_batch)
    session.commit()  

    for package in session.query(packages).all():
        package.status = "Dispatched"
        package.dispatchBatchID = new_dispatch_batch.id
    session.commit()
    session.close()
    return{"message" : "Dispatched successfully"}

def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name= username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False

    access_token = create_token(username=username,token_type="access",user_id=user.user_id,role=user.role,)
    refresh_token = create_token(username=username,token_type="refresh",user_id=user.user_id,role=user.role,)

    session.close()
    return {"access_token": access_token, "refresh_token": refresh_token}


def create_token(username, token_type, user_id, role):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "user_id": user_id,
        "role": role,
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time),
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return False
    if payload["token_type"] == token_type:
        return payload
    return False


#--------------Users-------------------
def register_user(user_name :str, password: str, role: str):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name = user_name).first()
    if user_exists is not None:
        session.close()
        return False

    try:
        hashed_password = ph.hash(password)
    except Exception:
        session.close()
        return False

    session.add(Users(user_name=user_name, password=hashed_password, role=role))
    session.commit()
    session.close()
    return True