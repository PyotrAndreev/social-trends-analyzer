from fastapi import FastAPI
from SPY_service.api.endpoints import channel, product, brand, video, advertisement
from SPY_service.database.database import init_ads_db

app = FastAPI()
init_ads_db()

app.include_router(channel.router, prefix="/channels", tags=["channels"])
app.include_router(product.router, prefix="/products", tags=["products"])
app.include_router(brand.router, prefix="/brands", tags=["brands"])
app.include_router(video.router, prefix="/videos", tags=["videos"])
app.include_router(advertisement.router, prefix="/advertisements", tags=["advertisements"])
