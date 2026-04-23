from app import app
from database import init_db
from routers import products, sales, api_key

# Initialize database
init_db()

# Include routers
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(api_key.router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Mire se vini ne Boxing Shop API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products",
            "sales": "/sales",
            "api_key": "/api-key",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
