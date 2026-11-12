from sqlalchemy import Integer, String, Column, create_engine,ForeignKey, DateTime
from sqlalchemy.orm import Session, declarative_base;
from datetime import datetime, timedelta, timezone;
from fastapi import HTTPException;
import jwt

DB_PATH = "study_room.db"

engine = create_engine(f"sqlite:///{DB_PATH}")
ACCESS_TOKEN_EXPIRY = 1
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
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

Base.metadata.create_all(engine)


def register_package(name, destination,weight):
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
    session.close()
    return {"message": "Package registered successfully"}

def verify_login(username, password):
    expected_username = os.environ.get("AUTH_USERNAME")
    expected_password = os.environ.get("AUTH_PASSWORD")
    if not expected_username or not expected_password:
        raise RuntimeError("AUTH_USERNAME and AUTH_PASSWORD must be configured")

    if hmac.compare_digest(username, expected_username) and hmac.compare_digest(password, expected_password):
        access_token = create_token(username=username, token_type="access")
        refresh_token = create_token(username=username, token_type="refresh")
        return {"access_token": access_token, "refresh_token": refresh_token}
    return False


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

def create_token(username, token_type):
    secret_key = os.environ.get("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY must be configured")
    if token_type == "access":
        expiry_minutes = ACCESS_TOKEN_EXPIRY
    elif token_type == "refresh":
        expiry_minutes = REFRESH_TOKEN_EXPIRY
    else:
        raise ValueError("Unsupported token type")

    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload=payload, key=secret_key, algorithm=ALGORITHM)


def verify_token(token, token_type="access"):
    secret_key = os.environ.get("JWT_SECRET_KEY")
    if not secret_key or not token:
        return False
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=[ALGORITHM])
    except (jwt.PyJWTError, TypeError, ValueError):
        return False
    if payload.get("token_type") == token_type:
        return payload.get("username")
    return False