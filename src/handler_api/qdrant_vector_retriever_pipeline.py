from langchain.vectorstores import Qdrant
from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from dotenv import load_dotenv
from langchain.schema.document import Document
import json 
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from typing import List,Tuple ,Union, Any, Dict
import qdrant_client
import os 
import logging 




class QdrantVectorRetrieverPipeline:

    @handle_exceptions
    def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict) -> None:
        """
        initializes qdrant client, embedder and vector store
        provides a foundation for instant/ready-to-use retrieval function
        """
        
        self.log_writer = AppLogger("DocumentToQdrantPipeline")
        self.client = None
        self.vector_store = Union[Qdrant, None] # update this to be Qdrant
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.embedder = self.initialize_embedding_func()

    @handle_exceptions
    def initialize_embedding_func(self):
        """
        Initializes the embedding function.

        :return: The initialized HuggingFaceEmbeddings object.
        """
        hf = HuggingFaceEmbeddings(
        model_name=self.model_name,
        model_kwargs=self.model_kwargs,
        encode_kwargs=self.encode_kwargs)

        embedding_dimension = hf.dict()['client'][1].get_config_dict()["word_embedding_dimension"]
        self.log_writer.handle_logging(f"embedder initialized with dimension: {embedding_dimension}" )
        #print("embedder initialized with dimension: ", embedding_dimension)

        return hf
        
    @handle_exceptions
    def initialize_qdrant_client(self, ):
        load_dotenv()
        QDRANT_URL = os.getenv('QDRANT_URL')
        QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
        QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')


        self.client = qdrant_client.QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY,)
            
        self.vector_store = Qdrant(
            client=self.client,
            collection_name=QDRANT_COLLECTION_NAME,
            embeddings=self.embedder)
        self.log_writer.handle_logging(f"Qdrant vector store initialized for collection: {QDRANT_COLLECTION_NAME}")


    async def similarity_search(self, query: Union[str, List[str]], k:int = 3, filter=None):
        print("query: ", query)
        print("filter: ", filter)
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
                #print(self.vector_store)
                results = self.vector_store.max_marginal_relevance_search(query, filter = filter, k=k)
                #print(results)
                if len(results)<1: # check if the response from database is empty.
                    self.log_writer.handle_logging(f"no results found for {query}", logging.ERROR)
                    return None
                return await self.post_process_results(results)
            except Exception as e:
                self.log_writer.handle_logging(f"similarity search failed with error: {e}", logging.ERROR)
                return None 

        else: 
            self.log_writer.handle_logging("query provided is not a string or a list of strings", logging.ERROR)
            return None
        
    
    async def post_process_results(self, search_results: List[Document]) -> List[Dict]:
 
        formatted_results = []
        for document in search_results:
            try:
                recipe = {
                    'recipe_name': document.metadata.get('recipe_name', 'No name available'),
                    'recipe_ingredients': document.metadata.get('recipe_ingredients_formatted', 'No ingredients available'),
                    'recipe_directions': document.metadata.get('recipe_directions_formatted', 'No directions available'),
                    'recipe_details': document.metadata.get('recipe_details_formatted', 'No details available'),
                    'recipe_nutrition_details': document.metadata.get('recipe_nutrition_details_formatted', 'No nutrition details available'),
                    'recipe_tags': document.metadata.get('recipe_tags_formatted', 'No tags available'),
                    'recipe_image_url': document.metadata.get('recipe_img_url-src', 'No image available'),
                    'recipe_url': document.metadata.get('recipe_card-href', 'No URL available')
                }
                formatted_results.append(recipe)
                print("OK")
            except AttributeError as e:
                # Handle the case where the document does not have the expected attributes
                self.log_writer.handle_logging(f"document {document} does not have the expected attributes, error: {e}", logging.ERROR)
                return None

        return formatted_results
    

def initialize_qdrant_vector_retriever():
    #MODEL PARAMETERS
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    pipeline = QdrantVectorRetrieverPipeline(model_name, model_kwargs, encode_kwargs)
    pipeline.initialize_qdrant_client()
    pipeline.log_writer.handle_logging("vector retriever pipeline initialized successfully!")
    return pipeline