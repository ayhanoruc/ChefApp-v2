from src.database.document_to_vectorstore_pipeline import DocumentToVectorStorePipeline
from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from typing import List, Dict, Union, Tuple

class VectorRetrieverPipeline(DocumentToVectorStorePipeline):

    def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict, overwrite: bool = False) -> None:
        super().__init__(model_name, model_kwargs, encode_kwargs, overwrite)
        self.log_writer = AppLogger("VectorRetrieverPipeline")

    @staticmethod
    def drop_duplicates(raw_text_list):
        """
        drops duplicates from a list of strings
        """
        return list(set(raw_text_list))
    
    @handle_exceptions
    async def post_process_results(self, search_results: List) -> List[Dict]:
            if search_results is None:
                return "No results found."
            #print("search results:\n", search_results )
            formatted_results = []

            for document in search_results:
                try:
                    recipe = {
                        'recipe_name': document.metadata.get('recipe_name', 'No name available'),
                        'recipe_ingredients': document.metadata.get('recipe_ingredients_formatted', 'No ingredients available'),
                        'recipe_directions': document.metadata.get('recipe_directions_formatted', 'No directions available'),
                        'recipe_nutrition_details': document.metadata.get('recipe_nutrition_details_formatted', 'No nutrition details available'),
                        'recipe_tags': document.metadata.get('recipe_tags_formatted', 'No tags available'),
                        'recipe_image_url': document.metadata.get('recipe_img_url-src', 'No image available'),
                        'recipe_url': document.metadata.get('recipe_card-href', 'No URL available')
                    }
                    formatted_results.append(recipe)
                except AttributeError:
                    return None
                    # Handle the case where the document does not have the expected attributes
                    #print("Missing attribute in document")
            

            return formatted_results

    @handle_exceptions
    async def similarity_search(self, query: Union[str, List[str]], k:int = 3, filter:Dict[str,str]=None, where:Dict[str,str]=None , where_document:Dict[str,str]=None)->List[Tuple[str, float]]:

        """
        Performs a similarity search on the given query and filters the results by metadata.

        Parameters:
        - query : The query/ies to search for.
        - k : The number of results to return.

        Returns:
        - A list of tuples containing the documents and their corresponding similarity scores.
        """
                
        if isinstance(query, list):
            query = "-".join(query) # concatenate list items to a string

        if isinstance(query, str):
            try:
                #print(f"query: {query} \n k: {k} \n filter: {filter} \n where: {where} \n where_document: {where_document}")
                results = await self.vector_store.amax_marginal_relevance_search(query, k=k, fetch=k, lambda_mult= 0.7, where= where, filter=filter, where_document=where_document)
                #print("similarity search is performed successfully!")
                #print(results)
                #return results
                #print(type(results))
                return await self.post_process_results(results)
            except Exception as e:
                #print("similarity search failed with error: ", e)
                return None 

        else: 
            raise ValueError("query must be a string or a list of strings")


def initialize_vector_retriver():
    #MODEL PARAMETERS
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    pipeline = VectorRetrieverPipeline(model_name, model_kwargs, encode_kwargs)
    pipeline.initalize_pinecone_store(index_name="chef-app")
    pipeline.log_writer.handle_logging("vector retriever pipeline initialized successfully!")
    return pipeline


async def run_vector_retriever_pipeline(vector_retriever:None,query: Union[str, List[str]], k:int = 3, filter:Dict[str,str]=None, where:Dict[str,str]=None , where_document:Dict[str,str]=None)->List[Tuple[str, float]]:
    
    results = await vector_retriever.similarity_search(query, k=k, filter=filter, where=where, where_document=where_document)
    vector_retriever.log_writer.handle_logging("results fetched for given query successfully!")
    return results



#https://docs.pinecone.io/docs/metadata-filtering
#https://www.mongodb.com/docs/manual/reference/operator/query/
#https://pypi.org/project/qdrant-client/
#https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/http/models/models.py
""" 
"filter": {
    "must": [
      {
        "key": "time_id",
        "range": {
          "lt": 1701770169349,
          "gt": 1693907769000
        }
      }]
  },

"""
#https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/http/models/models.py#L553
"""
class Filter(BaseModel, extra="forbid"):
    should: Optional[List["Condition"]] = Field(
        default=None, description="At least one of those conditions should match"
    )
    must: Optional[List["Condition"]] = Field(default=None, description="All conditions must match")
    must_not: Optional[List["Condition"]] = Field(default=None, description="All conditions must NOT match")

"""
#https://qdrant.tech/documentation/concepts/filtering/


#https://cloud.zilliz.com/signup
if __name__ == "__main__":
    query = [
        "chicken",
        "butter",
        "eggs",
    ]
    where_document_condition_2 ={
        "$and": [
            {"$contains": "dinner"},
            {"$contains": "Healthy"}
        ]
    }
    vector_retriever = initialize_vector_retriver()
    
    results = run_vector_retriever_pipeline(vector_retriever,query, where_document=where_document_condition_2)
    print(results)