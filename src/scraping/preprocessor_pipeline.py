from src.scraping.thirdparty.feature_extractor import pipeline_preprocessor
from src.logger import AppLogger
from src.exception_handler import handle_exceptions
from src.scraping.generic.generic_scraping import read_json, read_xlsx
from src.constants import pipeline_constants


import os , sys , logging
import shutil








class PreprocessorPipeline:

    """
    1- takes a .xlsx file_path to process
    2- checks if field names matching with intented field names
    3- if invalid, sends them to invalid_recipes_folder
    4- if valid:
        - calls run_preprocessor_pipeline
        - saves created json files to the same recipe directory. 
    
    """

    def __init__(self,file_path:str):

        self.log_writer = AppLogger("PreprocessorPipeline") # Initialize the logger

        #grasp unwanted fields
        self.unwanted_fields = pipeline_constants.UNIVERSAL_XLSX_UNWANTED_FIELDS
        #grasp wanted fields
        self.wanted_fields = pipeline_constants.UNIVERSAL_XLSX_WANTED_FIELDS
        
        self.file_path = file_path
        

    def validate_file(self):
        """
        checks if the file is valid according to universal_recipe_format 
        if not, returns False
        if valid, returns True
        """
        df = read_xlsx(self.file_path)
        field_names = df.columns # which is a list of field names
        for field in field_names:
            if field in self.unwanted_fields:
                df.drop(field, axis=1, inplace=True)
                field_names.remove(field)
        

        #turn them into set then check difference
        diff = set(field_names).difference(set(self.wanted_fields))
        if diff==set():
            self.log_writer.handle_logging(f"FILE VALIDATION SUCCESS for file {self.file_path}", logging.INFO)
            df.to_excel(self.file_path, index=False) # re-write the file
            return True    
        else:
            self.log_writer.handle_logging(f"FILE VALIDATION FAILED for file {self.file_path}, invalid fields: {diff}", logging.ERROR)
            return False


    def call_preprocessor(self):
        """
        calls the preprocessor
        """
        #call pipeline_preprocessor
        pipeline_preprocessor(self.file_path)
        
    def run_preprocessor_pipeline(self):
        """
        orchestrates the preprocessor pipeline
        """
        if self.validate_file():
            self.call_preprocessor()

        else: # invalid file
            #move the file to invalid_recipes_folder
            os.makedirs(pipeline_constants.INVALID_RECIPES_FOLDER, exist_ok=True)
            shutil.move(self.file_path, os.path.join(pipeline_constants.INVALID_RECIPES_FOLDER, os.path.basename(self.file_path)))
            self.log_writer.handle_logging(f"Moved invalid file {self.file_path} to {pipeline_constants.INVALID_RECIPES_FOLDER}", logging.INFO)




if __name__ == '__main__':
    test_file_path = r"C:\Users\ayhan\Desktop\ChefApp_v2\artifacts\recipes\new_data\2foodnet_formatted\foodnet_greek_formatted.xlsx"
    obj = PreprocessorPipeline(test_file_path)
    obj.run_preprocessor_pipeline()
