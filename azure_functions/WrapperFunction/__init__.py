from fastapi import HTTPException, status, APIRouter, FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Any, List, Optional
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import create_engine, Column, Integer, String, func as sqlunc
import azure.functions as func
import fastapi
from .models import *

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

# Pydantic model for request and response
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


router = APIRouter()
@router.get("/geonames/", response_model=List[GeoNameResponse])
async def read_geonames(
    city_name: str = Query(..., description="The name of the city."),
    country_code: Optional[str] = Query(None, description="The country code."),
):
    """
    Get geonames based on a city name and an optional country code.

    Parameters:
    - city_name (str): The name of the city.
    - country_code (str, optional): The country code.

    Returns:
    - List[GeoNameResponse]: List of geonames matching the city name and, optionally, the country code.
    """
    db = SessionLocal()

    try:
        query = db.query(GeoName).filter(sqlunc.lower(GeoName.name).startswith(sqlunc.lower(city_name)))

        if country_code is not None:
            query = query.filter(GeoName.country_code == country_code)

        geonames = (
            query
            .limit(10)
            .all()
        )

        if not geonames:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No geonames found for {city_name} in {country_code}" if country_code else f"No geonames found for {city_name}",
            )

        # Convert GeoName instances to GeoNameResponse instances if needed
        # geo_name_responses = [GeoNameResponse(**item.dict()) for item in geonames]
        return geonames
    finally:
        db.close()

@router.get("/geonames/getone/")
async def read_geonames(
    city_name: str = Query(..., description="The name of the city."),
):
    db = SessionLocal()

    # Order the results by Levenshtein distance, with the closest match first
    geonames = (
        db.query(GeoName)
        .filter(sqlunc.lower(GeoName.name).contains(sqlunc.lower(city_name)))
        .order_by(sqlunc.levenshtein(sqlunc.lower(GeoName.name), sqlunc.lower(city_name)))
        .first()
        .all()
    )

    db.close()

    if not geonames:
        raise HTTPException(status_code=404, detail="No geonames found")

    return geonames
app.include_router(router)
# Allow all origins during development, replace this with your actual frontend origin in production
origins = ["https://icy-forest-0ae3f0503.4.azurestaticapps.net"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
