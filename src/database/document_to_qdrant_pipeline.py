from src.database.vector_database import VectorRetriever
from langchain.vectorstores import Qdrant
from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from dotenv import load_dotenv
from langchain.schema.document import Document
import json 
from langchain.schema.document import Document
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from typing import List,Tuple ,Union, Any, Dict
import os 
from src.database.document_generator import JsonToDocument
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams,OptimizersConfig



#STEPS:
# 1. prepare environment keys
# 2. initialize qdrant client with keys
# 3. build vectorstore from documents 
# 4. add new documents

class DocumentToQdrantPipeline(VectorRetriever):
    """
    pass overwrite = True when creating the vector store for the first time and if you want to overwrite intentionally.
    pass overwrite = False otherwise.
    """
    def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict, overwrite: bool = False) -> None:

        super().__init__(model_name, model_kwargs, encode_kwargs, overwrite)
        self.log_writer = AppLogger("DocumentToQdrantPipeline")
        self.client = None
        self.vector_store = Union[Qdrant, None] # update this to be Qdrant
        # we will still be initializing huggingface embeddings.

    """
    doc_store = Qdrant.from_texts(
        texts, embeddings, url="<qdrant-url>", api_key="<qdrant-api-key>", collection_name="texts"
    )"""

    @handle_exceptions
    def initialize_qdrant_client(self, documents:List[Document]=None, ):
        load_dotenv()
        QDRANT_URL = os.getenv('QDRANT_URL')
        QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
        QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')

        if documents:
            self.vector_store = Qdrant.from_documents(documents, embedding=self.embedder, url=QDRANT_URL, api_key=QDRANT_API_KEY, collection_name=QDRANT_COLLECTION_NAME)

        else:
            self.client = qdrant_client.QdrantClient(
                url=QDRANT_URL, api_key=QDRANT_API_KEY,)
            

            optimizers_config = {
                "deleted_threshold": 0.2,
                "vacuum_min_vector_number": 1000,
                "default_segment_number": 0,
                "max_segment_size": None,
                "memmap_threshold": None,
                "indexing_threshold": 200,  # Set the indexing threshold 
                "flush_interval_sec": 5,
                "max_optimization_threads": 1
            }

            # Create or update the collection with the new configuration
            """self.client.create_collection(
                collection_name="chef-app",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                optimizers_config=optimizers_config
            )"""
            self.vector_store = Qdrant(
                client=self.client,
                collection_name=QDRANT_COLLECTION_NAME,
                embeddings=self.embedder
            )

    #No need to update add_documents, since langchain handles them automatically with the same implementation.

    def similarity_search(self, query: Union[str, List[str]], k:int = 3, filter=None):

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
                results = self.vector_store.max_marginal_relevance_search(query, filter=filter, k=k)
                #print("similarity search is performed successfully!")
                #print(results)
                #return results
                print(type(results))
                return self.post_process_results(results)
            except Exception as e:
                print("similarity search failed with error: ", e)
                return None 

        else: 
            raise ValueError("query must be a string or a list of strings")

def run_documents_to_qdrant_pipeline(documents:List[Document]):
        
    #MODEL PARAMETERS
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    pipeline = DocumentToQdrantPipeline(model_name, model_kwargs, encode_kwargs)
    pipeline.initialize_qdrant_client()
    pipeline.add_new_documents(documents)
    pipeline.log_writer.handle_logging("documents-to-qdrant-pipeline completed successfully!")


def initialize_vector_retriver():
    #MODEL PARAMETERS
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    pipeline = DocumentToQdrantPipeline(model_name, model_kwargs, encode_kwargs)
    pipeline.initialize_qdrant_client()
    pipeline.log_writer.handle_logging("vector retriever pipeline initialized successfully!")
    return pipeline

def run_retriever_pipeline(query, filter=None)->List[Document]:
    pipeline = initialize_vector_retriver()
    
    results = pipeline.similarity_search(query=query, filter=filter)
    #print(len(results))
    #print(type(results))
    print(results)


ingredients_list = [ 
        "cup butter",
        " plain yogurt",
        "sugar",
        "1  egg",
        "vanilla "]


#filter notes:
#create payload schema
#all you need: https://qdrant.tech/documentation/concepts/filtering/#match-any
#options: "text":substring match, "full-text":exact match
#use json/dict format and pass as filter to amax_marginal_relevance_search
#embrace must , must_not, should and any.
#can add multiple tags to filter inside must list.
#can add allergic ingredients to filter inside mustn_not list.
#include all of your tags, filtering values inside the page_content, otherwise you have to define a payload schema
#its too-practical with page_content




filter_1 = {
    "must": [
        { "key": "page_content", "match": {"text": "Fruit"} },
        { "key": "page_content", "match": {"text": "Breakfast"} },
        ],
    "must_not": [
        { "key": "page_content", "match": {"text": "sugar"} }]
}


#un_retriever_pipeline(ingredients_list, filter=filter_1)