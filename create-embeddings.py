from Classes import ChatGPT, Embeddings
from openai import OpenAI

import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

def create_embeddings(input_csv, embedding_model_name, embedding_encoding, max_tokens):
    # Create the ChatGPT object (embedding model general function is inside ChatGPT class)
    embedding_object = ChatGPT(embedding_model_name, "", [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    
    # get the embeddings
    input_dataframe = pd.read_csv(input_csv)
    embeddings_object = Embeddings(embedding_object, embedding_encoding, max_tokens)
    embeddings_dataframe = embeddings_object.get_embeddings(input_dataframe)

    # save the embeddings
    embeddings_dataframe.to_csv("datasets/reviews_with_embeddings_1k.csv", index=False)

def main():
    input_csv = "datasets/reviews_small.csv"
    embedding_model_name = "text-embedding-3-small"
    embedding_encoding = "cl100k_base"
    max_tokens = 8000 # the maximum for text-embedding-3-small is 8191
    create_embeddings(input_csv, embedding_model_name, embedding_encoding, max_tokens)

if __name__ == "__main__":
    main()