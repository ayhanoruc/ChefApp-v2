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


class VectorRetriever:
    """
    pass overwrite = True when creating the vector store for the first time and if you want to overwrite intentionally.
    pass overwrite = False otherwise.
    """
    def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict, overwrite: bool = False) -> None:

        
        # we can pass different vector stores instead of built-in implemented-Chroma option. but this may require further consideration.
        self.vector_store: Union[Chroma, None] = None
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.embedder = self.initialize_embedding_func()
        self.overwrite = overwrite
        

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
        print("embedder initialized with dimension: ", embedding_dimension)

        return hf

    def initialize_vector_store(self, persist_directory:str,collection_name:str, documents:List[Document]=None,):
        """
        Initializes a Chroma vector store with the given texts and collection name.
        if overwrite = True, the vector store will be overwritten or created if it does not exist.


        Args:
            persist_directory (str): The directory to persist the vector store.
            texts (List[str]): The list of texts to be stored in the vector store.
            collection_name (str): The name of the collection.

        Returns:
            Chroma: The initialized Chroma vector store.
        """
        if self.overwrite:
            if os.path.exists(persist_directory) and os.path.isdir(persist_directory):
                print("persist directory already exists")
            else: 
                os.mkdir(persist_directory, exist_ok=True)
                print("persist directory created")
        
            self.vector_store = Chroma.from_documents(
                        documents =documents , 
                        embedding=self.embedder,
                        collection_name= collection_name,
                        persist_directory=persist_directory)

            self.vector_store.persist()
        
        else:
            # if user wants to use an existing vector store as retriever. user doesnot need to pass any documents.
            self.vector_store = Chroma(persist_directory=persist_directory, embedding_function=self.embedder, collection_name=collection_name)

        print("chroma vector store initialized successfully, and ready for retrieval!")



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

        print("pinecone vector store initialized successfully, and ready for retrieval!")


    @staticmethod
    def drop_duplicates(raw_text_list):
        """
        drops duplicates from a list of strings
        """
        return list(set(raw_text_list))



    def similarity_search(self, query: Union[str, List[str]], k:int = 3, filter:Dict[str,str]=None, where:Dict[str,str]=None , where_document:Dict[str,str]=None)->List[Tuple[str, float]]:

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
                results = self.vector_store.max_marginal_relevance_search(query, k=k, fetch=k, lambda_mult= 0.7, where= where, filter=filter, where_document=where_document)
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




    def add_new_documents(self,documents:List[Document])->List[str]:

        """Adds new documents: a list of langchain Document objects to the vector store.
           Its better to be consistent with the metadata of the documents.
        """
        # we need to ensure that the documents are unique by their specific metadata(e.g. href)

        ids = self.vector_store.add_documents(documents)
        self.vector_store.persist()# make sure the changes to database are persisted -> inherent behaviour from sqlite3
        print("new documents added to the vector store ids:", ids)
        return ids


    def post_process_results(self, search_results: List[Document]) -> List[Dict]:
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
                # Handle the case where the document does not have the expected attributes
                print("Missing attribute in document")
        

        return formatted_results





    # Now, you need to implement the add_new_document method in VectorRetriever class to handle the metadata and vector insertion



if __name__ == "__main__":

    #1. Initialize your vector retriever with the appropriate model and arguments.
    #2. Initialize the JsonToDocument class.
    #3. specify the json_file_path
    #4. Process the JSON file to create a list of Document objects.
    #5. Initialize the vector store, if it's the first time or if you want to overwrite.
        # This step is usually done once, not every time you add new documents.

    #6. Add the new documents to the vector store.
        # This step is repeated every time you have new documents to add.

    #---------SEARCH---------
    #7. specify the ingredients list , concatanate it and pass it as a search query, 
    #8. Use the VectorRetriever to perform a similarity search with the query
    #9. Print the results

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}


    persist_directory = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\vector_db_4"
    os.makedirs(persist_directory, exist_ok=True)
    collection_name= "recipe_collection"

    

    
    

    #single document
    #json_file_path = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\cusine\italian\italian-desserts.json"
    #documents = json_to_document.process_json_document(file_path=json_file_path)
    
    recipes_dir_1 = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\new_data\allrecipescom"
    recipes_dir_2 = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\new_data\2foodnet_formatted"


    
    """
    json_to_document = JsonToDocument()

    categories_1 = os.listdir(recipes_dir_1)
    documents = []

    # allrecipes.com
    for category in categories_1:
        file_list = os.listdir(os.path.join(recipes_dir_1, category))
        for file in [file for file in file_list if file.endswith(".json")]:
            json_file_path = os.path.join(recipes_dir_1, category, file)
            documents.extend(json_to_document.process_json_document(file_path=json_file_path))

    # foodnet.com
    file_list = os.listdir(recipes_dir_2)
    for file in [file for file in file_list if file.endswith(".json")]:
        json_file_path = os.path.join(recipes_dir_2, file)
        documents.extend(json_to_document.process_json_document(file_path=json_file_path))


    print(len(documents),"documents found!", type(documents)) # created database from 12456 documents in 165 seconds.  """

    ####################### VECTORSTORE & RETRIEVAL ###############################################

    vector_retriever = VectorRetriever(model_name = model_name, model_kwargs= model_kwargs, encode_kwargs=encode_kwargs, overwrite=False)

    #using CHROMA
    # since overwrite is set to False, it will initialize the vector store as retriever.pass documents=None
    #vector_retriever.initialize_vector_store(persist_directory=persist_directory, documents=None, collection_name=collection_name)
    #vector_retriever.add_new_documents(documents=documents)

    #using PINECONE
    vector_retriever.initalize_pinecone_store(index_name="chef-app")# dont pass documents if you want to initialize an existing vector store
    

    
    ingredients_list = [ "cup butter",
            " plain yogurt",
            "sugar",
            "1  egg",
            "vanilla "]


    #where_document: Optional[Dict[str, str]]
    # source_code : https://github.com/chroma-core/chroma/blob/main/chromadb/api/types.py#L138

    
    where_condition = {
    "recipe_nutrition_details_formatted.Calories": {"$lte": 400}}


    where_document_condition_1 = {
        "$contains": "Turkish"}

    where_document_condition_2 ={
        "$and": [
            {"$contains": "dinner"},
            {"$contains": "Healthy"}
        ]
    }


    # Perform a similarity search
    results = vector_retriever.similarity_search(query=ingredients_list, k=10, where_document = where_document_condition_2)


    
    for result in results:
        #print(result)
        #print(type(result))
        print(json.dumps(result, indent=4))
        print("\n\n")


    # Document: (page_content, metadata) where metadata: dict
    """ 
    print(results[0].page_content)
    print(results[0].metadata.keys())
    print(results[0].metadata["recipe_name"]) 
    """
    print("DONE")
