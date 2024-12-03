import tiktoken
import numpy as np

class Embeddings():
    def __init__(self, embedding_object, embedding_encoding, max_tokens):
        self.__embedding_object = embedding_object
        self.__embedding_encoding = embedding_encoding
        self.__max_tokens = max_tokens
    
    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


    def __generate_embedding(self, text):
        try:
            self.__embedding_object.set_prompt(text)
            return self.__embedding_object.embedding_model()
        except Exception as e:
            print(f"Error generating embedding for text: {text[:50]}... Error: {e}")
            return None

    def get_embeddings(self, input_dataframe):
        # Get the encoding for the model
        encoding = tiktoken.get_encoding(self.__embedding_encoding)

        # Add a column for the number of tokens
        input_dataframe["n_tokens"] = input_dataframe["Text"].apply(lambda x: len(encoding.encode(x)))

        # Identify and log rows exceeding the token limit
        too_long_rows = input_dataframe[input_dataframe["n_tokens"] > self.__max_tokens]
        if not too_long_rows.empty:
            with open("excluded_rows.txt", "a") as f:
                for index, row in too_long_rows.iterrows():
                    f.write(f"Index: {index}\nText: {row['Text']}\nToken Count: {row['n_tokens']}\n\n")

        # Filter out rows exceeding the token limit
        input_dataframe = input_dataframe[input_dataframe["n_tokens"] <= self.__max_tokens]

        # Generate embeddings for the filtered dataframe
        input_dataframe["embedding"] = input_dataframe["Text"].apply(lambda text: self.__generate_embedding(text))
        return input_dataframe
        