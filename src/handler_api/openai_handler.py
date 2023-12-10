import yaml
from dotenv import load_dotenv
import os 
from openai import OpenAI

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
prompt = """

you are an helpful assistant that will format and translate the recipes provided to you. given the recipes, your strict- final format should be:
 "{'recipe_name':str
    'recipe_ingredients':List[str],
    'recipe_details':{'Prep_time':str, 'CookTime':str, 'TotalTime':str, 'Servings':str}
    'recipe_nutrition_details':{'Calories':str,'Total Fat':str,'Carbohydrates':str,'Protein':str},}'
  1- you can 'process'/'do calculation' etc on the data to achieve this final format. If you can not calculate, just 'make up' a reasonable value.
  2- you 'have to' satisfy the datatypes specified for each key-value pair!
  3- then you will translate this recipe to 'target' language."
"""



print(prompt)