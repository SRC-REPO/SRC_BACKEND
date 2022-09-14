from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model import Road
import fastapi

from logic import check_status

app = fastapi.FastAPI()

origins = [
    "*"
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


    
@app.get("/")
def home():
    return {"message": "Welecom Home!"}
    
@app.post("/check" ,response_model=Road)
def check(locations: List):
    return check_status(locations)


