# takes a list of Document objects
# initializes the vector store
# adds the documents to specified collection in the vector store

from typing import List, Tuple, Union
import json 
from langchain.schema.document import Document
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma, Pinecone
import pinecone
from typing import List,Tuple ,Union, Any, Dict
import os 
import ast
from src.database.document_generator import JsonToDocument
from dotenv import load_dotenv

from src.logger import AppLogger
from src.exception_handler import handle_exceptions

class DocumentToVectorStorePipeline:
    """
    pass overwrite = True when creating the vector store for the first time and if you want to overwrite intentionally.
    pass overwrite = False otherwise.
    """
    def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict, overwrite: bool = False) -> None:

        self.log_writer = AppLogger("DocumentToVectorStorePipeline")
        # we can pass different vector stores instead of built-in implemented-Chroma option. but this may require further consideration.
        self.vector_store: Union[Chroma, None] = None
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.embedder = self.initialize_embedding_func()
        self.overwrite = overwrite

        
    @handle_exceptions
    def initialize_embedding_func(self,):
        """
        Initializes the embedding function.

        :return: The initialized HuggingFaceEmbeddings object.
        """
        hf = HuggingFaceEmbeddings(
        model_name=self.model_name,
        model_kwargs=self.model_kwargs,
        encode_kwargs=self.encode_kwargs)

        embedding_dimension = hf.dict()['client'][1].get_config_dict()["word_embedding_dimension"]
        self.log_writer.handle_logging(f"embedder initialized with dimension: {embedding_dimension}")
        #print("embedder initialized with dimension: ", embedding_dimension)

        return hf

    @handle_exceptions
    def initalize_pinecone_store(self,index_name:str= "chef-app",  documents:List[Document]=None, ):
        load_dotenv()
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
        
        pinecone.init(
        api_key=PINECONE_API_KEY, 
        environment=PINECONE_API_ENV )

        index_name = "chef-app"

        if documents:
            self.vector_store = Pinecone.from_documents(documents, self.embedder, index_name=index_name) 
        else: 
            self.vector_store = Pinecone.from_existing_index(index_name=index_name, embedding=self.embedder)
        self.log_writer.handle_logging("pinecone vector store initialized successfully, and ready for CRUD operations!")
        
    @handle_exceptions
    def add_new_documents(self,documents:List[Document])->List[str]:

        """Adds new documents: a list of langchain Document objects to the vector store.
           Its better to be consistent with the metadata of the documents.
        """
        # we need to ensure that the documents are unique by their specific metadata(e.g. href)

        ids = self.vector_store.add_documents(documents)
        #self.vector_store.persist()# make sure the changes to database are persisted -> inherent behaviour from sqlite3
        self.log_writer.handle_logging(f"{len(documents)} documents inserted to the vector store successfully!")
        # print("new documents added to the vector store ids:", ids)
        return ids


def run_documents_to_pinecone_pipeline(documents:List[Document], overwrite:bool = False):
    """
    This function inserts new documents to the pinecone vector store.

    Args:
        documents (List[Document]): A list of documents to be inserted to the vector store.
        overwrite (bool, optional): If True, the vector store will be overwritten or created if it does not exist. Defaults to True.

    Returns:
        List[str]: A list of ids of the inserted documents.
    """
    #MODEL PARAMETERS
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}


    pipeline = DocumentToVectorStorePipeline(model_name, model_kwargs, encode_kwargs, overwrite)
    pipeline.initalize_pinecone_store(index_name="chef-app")
    pipeline.add_new_documents(documents)
    pipeline.log_writer.handle_logging("documents-to-pinecone-pipeline completed successfully!")

