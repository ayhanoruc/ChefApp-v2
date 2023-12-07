import os 


#LOGGING
LOGS_DIR = os.path.join(os.getcwd(), "logs")


#INVALID RECIPES
INVALID_RECIPES_FOLDER = os.path.join(os.getcwd(), "artifacts","invalid_recipes") # first make sure that it exists.


#RECIPE RELATED
UNIVERSAL_RECIPE_FORMAT_FILE = r"C:\Users\ayhan\Desktop\ChefApp_v2\src\universal_recipe_format.json"
UNIVERSAL_XLSX_UNWANTED_FIELDS = ["web-scraper-order","web-scraper-start-url","sub_category","sub","card","recipe_card"]
UNIVERSAL_XLSX_WANTED_FIELDS = ["recipe_card-href","recipe_tags","recipe_name","recipe_nutrition_details","recipe_image_url-src","recipe_ingredients","recipe_directions","recipe_details"]