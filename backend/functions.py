from sqlalchemy import Integer, String, Column, create_engine,ForeignKey, DateTime
from sqlalchemy.orm import Session, declarative_base;
from datetime import timedelta, datetime, timezone;
from fastapi import HTTPException;
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

DB_PATH = "warehouse.db"

engine = create_engine(f"sqlite:///{DB_PATH}")

USERNAME = "Toshimah"
PASSWORD = "123456789"
ACCESS_TOKEN_EXPIRY = 1
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
    user_name = Column(String)
    password= Column(String)
    
    
Base.metadata.create_all(engine)

# E1
def register_package(name, destination,weight):
    session = Session(engine)

    new_package = packages(
        name=name,
        destination=destination,
        weight=weight,
        arrival_date=datetime.now(),
        status="Pending_dispatched",
    )
    session.add(new_package)
    session.commit()
    session.close()
    return {"message": "Package registered successfully"}

# E2
def get_package_by_id(package_id):
    session = Session(engine)
    
    
    if not str(package_id).strip().isdigit():
        session.close()
        raise HTTPException(status_code=400, detail="Package ID must be a number")
    package_id = int(package_id)
        
    package = session.get(packages, package_id)
    
    if not package:
        session.close()
        raise HTTPException(status_code=404, detail="Package not found")
        
    response = {
        "package_id": package.package_id,
        "name": package.name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response

# E3
def update_package_details(package_id, name=None, destination=None, weight=None):
    session = Session(engine)
    package = session.get(packages, package_id)
    
    if not package:
        session.close()
        raise HTTPException(status_code=404, detail="Package not found")
    
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
    
    if not package:
        session.close()
        raise HTTPException(status_code=404, detail="Package not found")
    
    if package.status == "Dispatched":
        session.close()
        raise HTTPException(status_code=400, detail="Cannot delete a package that has already been dispatched")
    
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
        arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d")
        query = query.filter(packages.arrival_date == arrival_date)

    package_list = query.all()

    if not package_list:
        session.close()
        raise HTTPException(status_code=404, detail="Package not found")

    response = []
    for package in package_list:
        response.append({
            "id": package.package_id,
            "name": package.name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status,
        })

    session.close()
    return response

# E6
def view_dispatchBatches(destination=None, vehicle_number=None, dispatch_status=None):
    session = Session(engine)
    query = session.query(DispatchBatch)

    if destination is not None:
        query = query.filter(DispatchBatch.destination == destination)
    if vehicle_number is not None:
        query = query.filter(DispatchBatch.vehicle_number == vehicle_number)
    if dispatch_status is not None:
        query = query.filter(DispatchBatch.dispatch_status == dispatch_status)

    dispatch_batches_list = query.all()

    if not dispatch_batches_list:
        session.close()
        raise HTTPException(status_code=404, detail="DispatchBatch not found")

    response = []
    for dispatch_batch in dispatch_batches_list:
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

    total_packages = len(package_list)
    dispatched = 0
    pending = 0
    destination_count = {}

    for package in package_list:
        if package.status == "Dispatched":
            dispatched = dispatched + 1
        else:
            pending = pending + 1

        if package.destination in destination_count:
            destination_count[package.destination] = destination_count[package.destination] + 1
        else:
            destination_count[package.destination] = 1

    session.close()

    return {
        "total_packages": total_packages,
        "pending_dispatch": pending,
        "dispatched": dispatched,
        "destination_wise_count": destination_count,
    }


# E8
def create_dispatchBatches(destination, vehicle_number, dispatch_date=None):
    session = Session(engine)

    if dispatch_date is not None:
        dispatch_date = datetime.strptime(dispatch_date, "%Y-%m-%d")

    new_dispatch_batch = DispatchBatch(
        destination=destination,
        vehicle_number=vehicle_number,
        dispatch_status= "Dispatched",
        dispatch_date=dispatch_date,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    session.add(new_dispatch_batch)
    session.commit()
    session.close()

    return {"message": "Dispatch successfully"}


def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name= username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
        session.close()
    except VerifyMismatchError:
        return False
    session.close()
    access_token = create_token(username=username, token_type="access")
    refresh_token = create_token(username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}
    


def create_token(username, token_type):
    time = REFRESH_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload={
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc)+timedelta(minutes = time)   
        }
    token = jwt.encode(payload = payload , key = SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt= token, key = SECRET_KEY , algorithms=[ALGORITHM])
    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    return False 


#--------------Users-------------------
def register_user(user_name :str, password: str):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name = user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(Users(user_name = user_name, password = ph.hash(password)))
    session.commit()
    session.close()
    return True