from src.handler_api.qdrant_vector_retriever_pipeline import initialize_qdrant_vector_retriever
import json
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import List, Dict 
from src.logger import AppLogger
import openai 
from dotenv import load_dotenv
import requests
import os 
import httpx


retriever = initialize_qdrant_vector_retriever()

app_logger = AppLogger("UserEndpoint")


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

instruction_prompt = """
you are an helpful assistant that will format and translate the recipes provided to you. given the recipes, your strict- final format should be:
 "{'recipe_name':str
    'recipe_ingredients':List[str],
    'recipe_details':{'Prep_time':str, 'CookTime':str, 'TotalTime':str, 'Servings':str}
    'recipe_nutrition_details':{'Calories':str,'Total Fat':str,'Carbohydrates':str,'Protein':str},}'
  1- you can 'process'/'do calculation' etc on the data to achieve this final format. If you can not calculate, just 'make up' a reasonable value.
  2- you 'have to' satisfy the datatypes specified for each key-value pair!
  3- then you will translate this recipe to 'target' language."
  4- provide only the translated recipe. dont add any additional text since it will be used in production.
"""
openai.api_key = openai_api_key

url = "https://api.openai.com/v1/chat/completions"

headers = {
    'Authorization': f'Bearer {openai_api_key}',
    'Content-Type': 'application/json',}



async def call_gpt_2(instruction: str, prompt: str, model_name: str = "gpt-3.5-turbo", timeout_duration: int = 70) -> str:
    app_logger.handle_logging("Calling GPT for final processing.")
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ]
    }
    
    async with httpx.AsyncClient() as client:  # Use async client
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=timeout_duration)
            print(response)
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            return text
        except Exception as e:
            print(f"Error occurred: {e}")
            return None




async def call_gpt(instruction: str, prompt: str, model_name: str = "gpt-3.5-turbo", timeout_duration: int = 70) -> str:
    app_logger.handle_logging("Calling GPT for final processing.")
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ]
            }

    try:
        response = await requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout_duration)
        print(response)
        data = response.json()
        #print(data)
        
        text = data["choices"][0]["message"]["content"]
        #metrics = data["usage"]
        return text
    
    except requests.exceptions.Timeout:
        print(f"The request timed out after {timeout_duration} seconds.")
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
        return None



app = FastAPI()


@app.get("/home")
async def test_endpoint():
    return {"message":"ok"}

#create a request model
class UserRequest(BaseModel):
    country:str
    allergic_ingredients:List[str]
    preferences:List[str]
    ingredients:List[str]



@app.post("/get-recipe")
async def get_recipe(request:UserRequest):

    country = request.country
    allergic_ingredients = request.allergic_ingredients
    recipe_tags = request.preferences
    ingredients = request.ingredients

    query = f"{'|'.join(ingredients)}\nrecipe_tags_formatted{'|'.join(recipe_tags)}"
    filter_1 = {
        "must":[{"key":"page_content","match":{"text":tag}} for tag in recipe_tags],
        "must_not":[{"key":"page_content","match":{"text":ingredient}} for ingredient in allergic_ingredients]
     } 

    response = await retriever.similarity_search(
        query= query,
        filter=filter_1,
        k=1,
        )

    final_response = await call_gpt_2(instruction_prompt, response)
    
    return JSONResponse(content=final_response)
        



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,)