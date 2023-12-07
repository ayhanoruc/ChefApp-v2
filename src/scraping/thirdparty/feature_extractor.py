from src.exception_handler import handle_exceptions
from src.logger import AppLogger

import os
import re
import pandas as pd
from typing import List
import logging


class Preprocessor:
    def __init__(self) -> None:
        print("preprocessor initialized")
        self.df = pd.DataFrame([])  # initialize an empty dataframe
        self.file_path = None
        self.log_writer = AppLogger("Preprocessor")

    @handle_exceptions
    def read_xlsx(self, file_path: str, index_col=False) -> None:
        """
        reads excel file and performs initial data cleaning
        """
       
        sub_category = file_path.split("\\")[-1].split(".")[0]
        self.file_path = file_path

        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path , header=0, index_col=None)
        
        # Remove duplicated rows, if any
        df.drop_duplicates(inplace=True)

        # Remove rows with null values in "recipe_directions" column
        df.dropna(subset=["recipe_directions"], inplace=True)

        # Add a "sub_category" column derived from the file name
        df["sub_category"] = sub_category

        # Assign the final processed DataFrame to self.df
        self.df = df

       


    @handle_exceptions
    def df_to_json(self, path: str = None) -> None:
        """
        Converts a given record file in .xlsx format to JSON format.
        """
        if path is None:
            path = os.path.splitext(self.file_path)[0] + ".json"

        if self.df.empty:
            raise ValueError("DataFrame is empty. Please use read_xlsx to populate the DataFrame first.")

        self.df.to_json(path, orient="records", indent=4)

        self.log_writer.handle_logging(f"JSON file created at {path}", logging.INFO)


    @handle_exceptions
    def image_url_parser(self, image_url: str) -> str:
        """
        extracts https to .jpeg from image_url
        """
        #print(image_url)
        pattern = r'https[^"]+\.jpg'
        match = re.findall(pattern, image_url)
        if match:
            return match[0]
        return None

    @handle_exceptions
    def df_img_url_parser(self,) -> None:
        #remove rows with no image_url
        self.df.dropna(subset=["recipe_image_url-src"], inplace=True)
        self.df["image_url_formatted"] = self.df["recipe_image_url-src"].apply(self.image_url_parser)
        
        

    def recipe_tag_formatter(self) -> None:

        self.df.drop(self.df[self.df["recipe_tags"].isnull()].index, inplace=True)  # remove rows with no recipe_tags
        
        self.df["recipe_tags_formatted"] = self.df["recipe_tags"].apply(lambda tags: [kv["recipe_tags"] for kv in eval(tags)])
        # Get the common sub_category value
        common_sub_category = self.df["sub_category"].iloc[0]
        
        # Append the common_sub_category to each list in the "recipe_tags_formatted" column
        self.df["recipe_tags_formatted"] = self.df["recipe_tags_formatted"].apply(lambda element: element + [common_sub_category])


    @handle_exceptions
    def recipe_details_table_formatter(self) -> None:
        
        # leave it as list. gpt will take care of it. 
        self.df["recipe_details_formatted"] = self.df["recipe_details"].apply(lambda details: [kv["recipe_details"] for kv in eval(details)]) 
        



    @handle_exceptions
    def recipe_ingredients_formatter(self) -> None:

        # Drop rows with None or empty ingredient lists
        self.df = self.df.dropna(subset=["recipe_ingredients"])

        self.df["recipe_ingredients_formatted"] = self.df["recipe_ingredients"].apply(lambda tags: [kv["recipe_ingredients"] for kv in eval(tags)]) # already a list
        
        #self.df["recipe_ingredients_formatted"] = self.df["recipe_ingredients_formatted"].apply(lambda ingredient_list: self.ingredient_list_formatter(ingredient_list))


    @handle_exceptions
    def recipe_directions_formatter(self) -> None:
    
        self.df.dropna(subset=["recipe_directions"], inplace=True)# remove rows with no recipe_directions

        self.df["recipe_directions_formatted"] = self.df["recipe_directions"].apply(lambda tags: [kv["recipe_directions"] for kv in eval(tags)])



    @handle_exceptions
    def recipe_nutrition_details_formatter(self) -> None:

        self.df.dropna( subset=["recipe_nutrition_details"] , inplace=True)# remove rows with no recipe_nutrition_details

        #leave it as list. gpt will take care of it.
        self.df["recipe_nutrition_details_formatted"] = self.df["recipe_nutrition_details"].apply(lambda tags: [kv["recipe_nutrition_details"] for kv in eval(tags)])

        #self.df["recipe_nutrition_details_formatted"] = self.df["recipe_nutrition_details_formatted"].apply(lambda element: self.recipe_nutrition_formatter(element))

    @handle_exceptions
    def remove_unwanted_cols(self) -> None:
        self.df.drop(columns=["recipe_tags", "recipe_details", "recipe_ingredients", "recipe_directions", "recipe_nutrition_details"], inplace=True)


def pipeline_preprocessor(file_path:str)->pd.DataFrame:
    preprocessor = Preprocessor()
    df = preprocessor.read_xlsx(file_path)
    preprocessor.df_img_url_parser() 
    preprocessor.recipe_tag_formatter() 
    preprocessor.recipe_details_table_formatter() 
    preprocessor.recipe_ingredients_formatter() 
    preprocessor.recipe_directions_formatter()
    preprocessor.recipe_nutrition_details_formatter()
    preprocessor.remove_unwanted_cols()
    preprocessor.df_to_json() # turn each row-recipe into a json object and save it in a json file in the same directory as the .xlsx file
    return preprocessor.df

if __name__ == "__main__":
    #recipes-directory
    #iterate thru files end with .xlsx
    #define file_path
    #call pipeline_preprocessor

    recipes_dir = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\new_data\chineese"
    categories = os.listdir(recipes_dir)

    for category in [category for category in categories if category.endswith(".xlsx")]:
        path = os.path.join(recipes_dir, category) # ../breakfast/breakfast_breakfast-casseroles.xlsx
        print(path)
        pipeline_preprocessor(path)

    # OR ITERATE THRU CATEGORIES
    #recipes_dir = r"C:\Users\ayhan\Desktop\ChefApp\artifacts\recipes\new_data"

    """
    categories = os.listdir(recipes_dir)


    for category in categories:
        files = os.listdir(os.path.join(recipes_dir, category))

        for file in [file for file in files if file.endswith(".xlsx")]:
            path = os.path.join(recipes_dir, category, file)
            print(path)
            pipeline_preprocessor(path, features_to_use, unwanted_cols)
    """