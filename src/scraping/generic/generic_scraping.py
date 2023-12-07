import pandas as pd 
import os 
import re
import json 
from typing import List,Dict , get_args, get_origin, Type

def read_xlsx(file_path:str)->pd.DataFrame:
    df = pd.read_excel(file_path, header=0)
    print(df.info())
    return df 



        
def record_to_json(path:str):
    """
    Converts a given record file in .xlsx format to JSON format.

    Parameters:
    - path (str): The path to the record file.

    Returns:
    None
    """
    json_path = os.path.splitext(path)[0]+".json"
    data = read_xlsx(path).to_json(json_path,orient="records", indent=4) # here indent=4 makes it prettier
    print(f"Data saved to {json_path}")

    
def read_json(path:str):
    with open(path, 'r') as f:
        data = json.load(f)
        
    return data 

def is_of_type(obj, type_hint):
    """
    Check if the object conforms to the provided type hint.
    
    :param obj: The object to check.
    :param type_hint: The type hint against which to check the object.
    :return: True if the object is of the specified type hint, otherwise False.
    """
    # If the type hint is a generic (e.g., List[int]),
    # compare the origin (e.g., list) and the args (e.g., int).
    if hasattr(type_hint, '__origin__'):
        origin = get_origin(type_hint)
        args = get_args(type_hint)
        
        # Check if the object is of the origin type (e.g., list)
        if not isinstance(obj, origin):
            return False
        
        # If there are arguments (type parameters), check each element of the object
        if args:
            return all(isinstance(item, args[0]) for item in obj)
        return True
    
    # If the type hint is a regular type (e.g., int), use isinstance directly.
    return isinstance(obj, type_hint)




# EXAMPLE USAGE OF URL PARSER FUNCS.
#path = r'C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\breakfast\breakfast-cereals.json'
"""json_text = read_json(path)

card_info = json_text[2]["recipe_card"] 
url = json_text[2]["recipe_card-href"] # recipe url
print(image_url_parser(card_info)) # recipe image
print(url)"""

#features = ["recipe_card","recipe_card-href","recipe_tags","recipe_name","recipe_servings","recipe_prep_time","recipe_cook_time","recipe_total_time","recipe_nutrition","recipe_ingredients","recipe_directions"]




#recipes_dir = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes"

#categories = os.listdir(recipes_dir)

"""for category in categories:

    file_names: List = [name for name in  os.listdir(os.path.join(recipes_dir,category)) if name.endswith(".xlsx")]
    print(category,"/////////////////////")
    for file in file_names:
        print(file)
        path = os.path.join(recipes_dir,category,file)
        record_to_json(path)"""




