import json 

from langchain.schema.document import Document
from typing import List , Dict, Union
 


class JsonToDocument:
    """
    Takes a JSON file and returns a list of Langchain Document objects.
    
    """
    def __init__(self):

        print("JsonToDocument object initialized successfully!")# this should be logging instead

    
    
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



    def process_json_document(self,file_path:str)->List[Document]:
        """
        Process a JSON document and return a list of Document objects.
        """ 
        # load the JSON data: list of recipe dictionaries derived from .xlsx file
        with open(file_path, 'r') as f:
            json_data = json.load(f) 
            # we should make the loaded json prettier via json.dumps(json_data, indent=4)
        json_data = self.replace_null(json_data)
        
        print("json document is loaded successfully!")
        documents = []

        # Process each recipe in the JSON data
        for recipe in json_data:
            metadata, tags = self.extract_metadata(recipe)
            #print(type(metadata))
            ingredients_list = self.extract_ingredients_text(recipe)
            ingredients_text = "|".join(ingredients_list) # concatenate list items to a string, we may use "|" to seperate ingredient elements.
            document_text = f"{ingredients_text}\nrecipe_tags_formatted:{tags}" # concatenate metadata and ingredients_text for tag filtering during retrieval.
            # Construct a new Document object
            new_document = Document(
                metadata=metadata,
                page_content=document_text,)
                # add additional fields, if necessary

            documents.append(new_document) # we use append since we are adding documents one by one
            
        print("Documents are generated successfully! # of documents: ", len(documents))
        return documents

    def extract_metadata(self, recipe: Dict) -> Dict:
        """Extract the metadata from a recipe."""
        # Update the fields to match the keys in the JSON structure
        metadata_fields = ['recipe_card-href', 'recipe_tags_formatted', 'recipe_name', 'recipe_img_url-src',
                        'recipe_details_formatted', 'recipe_ingredients_formatted', 
                        'recipe_directions_formatted', 'recipe_nutrition_details_formatted']

        # Extract metadata and handle missing fields by setting them to None
        metadata = {field: str(recipe.get(field, "None")) for field in metadata_fields}
        tags = recipe.get('recipe_tags_formatted', "None")

        print("Metadata is extracted successfully!")
        return metadata, tags

    """def extract_metadata(self, recipe: Dict) -> Dict:
        #Extract the metadata from a recipe.
        # the fields to be included in the metadata
        metadata_fields = ['recipe_card','recipe_card-href', 'recipe_tags','recipe_name','recipe_servings', 
                            'recipe_prep_time', 'recipe_cook_time', 'recipe_total_time','recipe_nutrition','recipe_directions']
        
        # we may handle edge cases here, e.g. if a field is missing: replace with NULL| raise exception ???
        print("metadata is extracted successfully!")
        return {field: recipe[field] for field in metadata_fields if field in recipe} """

    def extract_ingredients_text(self, recipe: Dict) -> List:
        """Extract ingredients text: list of strings from a recipe."""
        # Directly return the list of ingredients from the recipe
        return recipe.get('recipe_ingredients_formatted', [])


    """ def extract_ingredients_text(self, recipe: Dict) -> List:
        #Extract and concatenate ingredients text: list of dicts from a recipe.
        # Concatenate ingredients into a single text string
        ingredients: List[dict] = recipe.get('recipe_ingredients', [])

        ingredients = json.loads(ingredients)

        # Initialize an empty list to store only the values.
        final_ingredients_list = []
        #print(ingredients, type(ingredients))
        for ingredient in ingredients: # here ingredient is a dictionary, bad naming...

            # This assumes that each ingredient dictionary has a 'recipe_ingredients' key.
            #print(ingredient)
            ingredient_text = ingredient['recipe_ingredients']

            # Decode the Unicode escape sequences in the ingredient string.
            # The 'unicode-escape' codec decodes the string with escape sequences into the actual characters.
            decoded_ingredient_text = bytes(ingredient_text, 'utf-8').decode('unicode-escape')
            final_ingredients_list.append(decoded_ingredient_text)

        #print(final_ingredients_list)

        return final_ingredients_list """


