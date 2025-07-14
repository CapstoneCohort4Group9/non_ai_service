from fastapi import FastAPI
from endpoints import router as api_router

app = FastAPI(title="Airline & Travel API")
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
