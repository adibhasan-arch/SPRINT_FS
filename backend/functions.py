from sqlalchemy import Integer, String, Column, create_engine,ForeignKey, DateTime
from sqlalchemy.orm import Session, declarative_base;
from datetime import date, datetime;
from fastapi import HTTPException;


DB_PATH = "study_room.db"

engine = create_engine(f"sqlite:///{DB_PATH}")
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
    dispatch_status = Column(String, default="none")
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

