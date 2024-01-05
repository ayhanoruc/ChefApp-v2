from src.database.document_generator_pipeline import DocumentGeneratorPipeline
from src.database.document_to_qdrant_pipeline import run_documents_to_qdrant_pipeline
import os

#iterates thru all the json recipes folder
#pass them to the document generator pipelineü
#then passes these documents to the run_documents_to_qdrant_pipeline to insert them into qdrant cloud


recipes_dir_1 = r"C:\Users\ayhan\Desktop\ChefApp_v2\artifacts\recipes\new_data\2foodnet_formatted"
recipes_dir_2 = r"C:\Users\ayhan\Desktop\ChefApp_v2\artifacts\recipes\new_data\allrecipescom"

pipeline = DocumentGeneratorPipeline()
#docs = pipeline.run_document_generator_pipeline(json_path)
documents = []

#iterate thru recipes_dir_1


for filename in os.listdir(recipes_dir_1):
    if filename.endswith(".json"):
        json_path = os.path.join(recipes_dir_1, filename)
        docs = pipeline.run_document_generator_pipeline(json_path)
        documents.extend(docs)

#iterate thru recipes_dir_2, this includes recipe folders
# Iterate through recipes_dir_2
for folder in os.listdir(recipes_dir_2):
    folder_path = os.path.join(recipes_dir_2, folder)
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                json_path = os.path.join(folder_path, filename)
                docs = pipeline.run_document_generator_pipeline(json_path)
                documents.extend(docs)

#then pass these documents to the run_documents_to_qdrant_pipeline
run_documents_to_qdrant_pipeline(documents)