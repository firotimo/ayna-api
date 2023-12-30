import azure.functions as func
import fastapi
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List
import uvicorn
from typing import Any
from sqlalchemy import Column, Integer, String, Float
app = fastapi.FastAPI()


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Root12zdz@bddkokatic.postgres.database.azure.com:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class GeoName(Base):
    __tablename__ = 'geonamespop'

    geonameid = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    asciiname = Column(String)
    alternatenames = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    feature_class = Column(String)
    feature_code = Column(String)
    country_code = Column(String)
    cc2 = Column(String)
    admin1_code = Column(String)
    admin2_code = Column(String)
    admin3_code = Column(String)
    admin4_code = Column(String)
    population = Column(Integer)
    elevation = Column(Integer)
    dem = Column(String)
    timezone = Column(String)
    modification_date = Column(String)
class GeoNameRequest(BaseModel):
    geonameid: int
    name: str
    asciiname: str
    alternatenames: List[str]
    latitude: float
    longitude: float
    feature_class: str
    feature_code: str
    country_code: str
    cc2: List[str]
    admin1_code: str
    admin2_code: str
    admin3_code: str
    admin4_code: str
    population: int
    elevation: int
    dem: str
    timezone: str
    modification_date: str
class GeoNameResponse(BaseModel):
    geonameid: int
    name: str
    asciiname: str
    alternatenames: str
    latitude: float
    longitude: float
    feature_class: str
    feature_code: str
    country_code: str
    cc2: Any
    admin1_code: str
    admin2_code: Any
    admin3_code: Any
    admin4_code: Any
    population: int
    elevation: Any
    dem: str
    timezone: str
    modification_date: Any

@app.get("/geonames/{city_name}", response_model=GeoNameResponse)
async def read_geoname(city_name: str):
    db = SessionLocal()
    geoname = db.query(GeoName).filter(GeoName.name == city_name, GeoName.population > 0).first()
    print(geoname)
    db.close()
    if geoname is None:
        raise HTTPException(status_code=404, detail="Geoname not found")
    return geoname