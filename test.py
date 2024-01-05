from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain.embeddings.fastembed import FastEmbedEmbeddings
import os 

load_dotenv()
embeddings = FastEmbedEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
document_embeddings = embeddings.embed_documents(
    ["This is a document", "This is some other document"]
)
print(len(document_embeddings[0]))