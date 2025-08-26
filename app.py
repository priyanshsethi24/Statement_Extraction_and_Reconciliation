from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.dolphin_router import router
from common.logs import logger
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
app_host = os.getenv("APP_HOST", "0.0.0.0")
app_port = int(os.getenv("APP_PORT", 5000))

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    logger.info('--- Started app ---')
    return {"message": "Hello, World!", "usage": ["/extract_statement"]}

if __name__ == '__main__':
    uvicorn.run(app, host=app_host, port=app_port)
    logger.info("--- Started app.py ---")
