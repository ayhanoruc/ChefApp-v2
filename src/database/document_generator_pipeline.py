import json 
from langchain.schema.document import Document
from typing import List , Dict, Union, Tuple
from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from src.constants import pipeline_constants
from src.database.document_to_vectorstore_pipeline import run_documents_to_pinecone_pipeline


import logging



class DocumentGeneratorPipeline:
    """
    Takes a JSON file and returns a list of Langchain Document objects.
    Steps:
        1- load the JSON data: list of recipe dictionaries derived from .xlsx file
        2- process each recipe in the JSON data, extract metadata and ingredients
        3- construct a new Document object and return list of Document objects
    """

    def __init__(self,):
        self.log_writer = AppLogger("DocumentGeneratorPipeline")

    @handle_exceptions
    def replace_null(self, obj:Union[Dict, List], fill_value = 'null')->Union[Dict, List]:
        """
        Recursively replaces all occurrences of `None` with the string `'null'` in a given JSON object.
        """
        if isinstance(obj, dict):
            return {k: self.replace_null(v) for k, v in obj.items()} # call replace_null for each item
        elif isinstance(obj, list):
            return [self.replace_null(v) for v in obj]
        elif obj is None:
            return fill_value
        else:
            return obj

    @handle_exceptions
    def load_json_object(self,file_path:str):
        with open(file_path, "r") as f:
            return json.load(f)

    
    @handle_exceptions
    def process_json_document(self, file_path:str)->List[Document]:
        """
        Process a JSON document and return a list of Document objects.
        """
        #load and clean the recipes in the JSON file
        json_data = self.replace_null(self.load_json_object(file_path))
        
        #initialize the Documents List
        documents = []

        for recipe in json_data:
            metadata, tags = self.extract_metadata(recipe)
            ingredients_list = self.extract_ingredients_text(recipe)
            ingredients_text = "|".join(ingredients_list) # concatenate list items to a string, we may use "|" to seperate ingredient elements.
            document_text = f"{ingredients_text}\nrecipe_tags_formatted:{tags}" # concatenate metadata and ingredients_text for tag filtering during retrieval.
            
            # Construct a new Document object
            new_document = Document(
                metadata=metadata,
                page_content=document_text,)
                # add additional fields, if necessary

            documents.append(new_document) # we use append since we are adding documents one by one
        self.log_writer.handle_logging(f"Documents are generated successfully! # of documents: {len(documents)}", logging.INFO)
        return documents

    @handle_exceptions
    def extract_metadata(self, recipe:Dict)->Tuple[Dict, str]:
        """
        Extract metadata from a recipe dictionary.
        """
        fields = pipeline_constants.UNIVERSAL_JSON_WANTED_FIELDS #formatted field names.
        #print(set(fields).difference(set(recipe.keys())))

        #extract key-value pairs using dict comprehension
        #metadata = {field: str(recipe.get(field),"None") for field in fields}#we want all the metadata to be strings
        metadata = {field: str(recipe.get(field, "None").decode('utf-8')) if isinstance(recipe.get(field), bytes) else str(recipe.get(field, "None")) for field in fields}

        tags = recipe.get("recipe_tags_formatted","None")
        return metadata, tags

    
    @handle_exceptions
    def extract_ingredients_text(self, recipe:Dict)->List:
        """
        Extract ingredients text: list of strings from a recipe.
        """
        ingredients_list = recipe.get("recipe_ingredients_formatted","None")
        return ingredients_list
        

    def run_document_generator_pipeline(self, file_path:str)->List[Document]:
        """
        Run the document generator pipeline.
        """
        return self.process_json_document(file_path)

if __name__ == "__main__":

    json_path = r"artifacts/recipes/new_data/2foodnet_formatted/foodnet_breakfast_formatted.json"
    
    pipeline = DocumentGeneratorPipeline()
    docs = pipeline.run_document_generator_pipeline(json_path)
    run_documents_to_pinecone_pipeline(docs)
    #print(docs[0].page_content)

