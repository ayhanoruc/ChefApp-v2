import json
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import uvicorn

from pydantic import BaseModel


import asyncio 

from src.database.vector_database import VectorRetriever
from typing import List, Dict 





model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}


persist_directory = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\vector_db_4"
collection_name= "recipe_collection"

#INITIALIZE the VECTOR RETRIEVER and make it ready as a global variable
vector_retriever_chroma = VectorRetriever(model_name = model_name, model_kwargs= model_kwargs, encode_kwargs=encode_kwargs, overwrite=False)
vector_retriever_chroma.initialize_vector_store(persist_directory=persist_directory, documents=None, collection_name=collection_name)
print("chroma vector retriever initialized successfully!")


vector_retriever_pinecone = VectorRetriever(model_name = model_name, model_kwargs= model_kwargs, encode_kwargs=encode_kwargs, overwrite=False)
vector_retriever_pinecone.initalize_pinecone_store(index_name="chef-app")
print("pinecone vector retriever initialized successfully!")

# this will contain the preferences of the user
params= {

    "ingredients_list":[
        "cup butter",
        " plain yogurt",
        "sugar",
        "1  egg",
        "vanilla "
    ],
    "recipe_tags": ["Dessert", "Healthy", "Italian"]
}


#pydantic data structure for the request payloads
class RecipeRequest(BaseModel):
    ingredients_list: List[str]
    recipe_tags: List[str]


# Dependency function for chroma
def get_vector_retriever_chroma():
    return vector_retriever_chroma

# Dependency function for pinecone
def get_vector_retriever_pinecone():
    return vector_retriever_pinecone



app = FastAPI()

@app.get("/home")
async def test_endpoint():

    return {"message":"ok"}





### ASYNC ### 
async def find_recipe_async(ingredients_list: List, k: int = 3, filter: Dict[str, str] = None, where: Dict[str, str] = None, where_document: Dict = None) -> List[Dict]:
    """
    Asynchronous function to handle metadata filtering and similarity search,
    then returns the most relevant documents.
    """
    vector_retriever = get_vector_retriever_pinecone() # take this as parameter
    #vector_retriever = get_vector_retriever_chroma()
    # Asynchronously perform the similarity search
    results = await asyncio.to_thread(
        vector_retriever.similarity_search,
        query=ingredients_list,
        k=k,
        filter=filter,
        where=where,
        where_document=where_document
    )
    return results


@app.post("/get-recipe")
async def get_recipe(request_body: RecipeRequest):
    try:
        ingredients_list = request_body.ingredients_list
        recipe_tags = request_body.recipe_tags
        where_document = {"$and": [{"$contains": tag} for tag in recipe_tags]}
        
        results = await find_recipe_async(ingredients_list=ingredients_list, where_document=where_document)
        response_message = f"You have asked for a {' | '.join(recipe_tags)} meal, and you have the following items: {' | '.join(ingredients_list)}"
        final_response = f"{response_message}\nHere are the results:\n{json.dumps(results, indent=2)}"
        return JSONResponse({"response": final_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



#THIS IS NOT NEEDED IN PRODUCTION

if __name__ == "__main__":
    
    uvicorn.run("api_handler:app", host="0.0.0.0", port=8000, reload=True)