from fastapi import APIRouter,  HTTPException
from SPY_service.database.db_API import DBAPI
from SPY_service.schemas.brand import Brand, BrandCreate

router = APIRouter()

@router.post("/", response_model=Brand)
def create_brand_endpoint(brand: BrandCreate):
    with DBAPI() as db_api:
        return db_api.create_brand(brand)

@router.get("/{brand_id}", response_model=Brand)
def get_brand_endpoint(brand_name: str):
    with DBAPI() as db_api:
        db_brand = db_api.get_brand(brand_name)
        if not db_brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return db_brand

@router.get("/", response_model=list[Brand])
def get_brands_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_brands(skip=skip, limit=limit)