import json 
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import uvicorn

from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from src.database.vector_retriever_pipeline import initialize_vector_retriver,run_vector_retriever_pipeline

from typing import List, Dict
import logging

vector_retriever = initialize_vector_retriver()
app_logger = AppLogger("UserEndpoint")

app = FastAPI()


@app.get("/home")
async def test_endpoint():
    return {"message":"ok"}

#create a request model
#fields: country:str, allergic_ingredients:List[str], preferences:List[str], ingredients:List[str]
class UserRequest(BaseModel):
    country:str
    allergic_ingredients:List[str]
    preferences:List[str]
    ingredients:List[str]


@app.post("/get-recipe")
async def get_recipe(request:UserRequest):
    try:
        country = request.country
        allergic_ingredients = request.allergic_ingredients
        recipe_tags = request.preferences
        ingredients = request.ingredients

        query = f"{'|'.join(ingredients)}\nrecipe_tags_formatted{'|'.join(recipe_tags)}"
        where_document = {"$and": [{"$contains": tag} for tag in recipe_tags]}
        filter_2 = {"$nin":["eggs"]}

        #handle negative-filtering for allergic ingredients
        #...
        allergic_filter =  {"$not_contains": "egg"}

        response = await run_vector_retriever_pipeline(
            vector_retriever=vector_retriever,
            query= query,
            where_document=allergic_filter)
        return JSONResponse(content=response)
        
    except Exception as e:
        app_logger.handle_logging(str(e),logging.ERROR)
        raise HTTPException(status_code=500, detail=str(e))
    