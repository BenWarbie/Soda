from fastapi import FastAPI
from .routes import trading

app = FastAPI(title="Soda Trading API")

# Include routers
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
