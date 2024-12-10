from Classes import ChatGPT, Prompts, WebScraper, TextExtractor, Embeddings

# ai act : 2-16: prohibited, 17-28: high risk, 29-30: limited risk, 31-32: minimal risk

from openai import OpenAI
import re
import ast
import openpyxl
import pandas as pd
import numpy as np
from ast import literal_eval

import os
from dotenv import load_dotenv
load_dotenv()

TOTAL_USE_CASES = 4

def prompt_approach():
    sheet = openpyxl.load_workbook("raw-dealroom.xlsx")["Sheet1"]
    model_name = "chatgpt-4o-latest"
    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    # sheet.max_row + 1
    for row in range(12, 21):
        url = sheet.cell(row=row, column=4).value
        startup_name = sheet.cell(row=row, column=2).value

        # Initialize the objects
        web_scraper_obj = WebScraper(url)
        prompts_obj = Prompts(TOTAL_USE_CASES)
        ai_use_cases = []

        print(f"URL: {web_scraper_obj.get_url()}")
        
        # Load page, get the content and links
        web_scraper_obj.load_page()
        page_content = web_scraper_obj.get_page_content(model_name)
        page_links = web_scraper_obj.get_page_links()


        # Use chat model to get relavant links
        chat_links_obj = ChatGPT(model_name, prompts_obj.get_important_links(page_links), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_links_response, input_tokens, output_tokens = chat_links_obj.chat_model()
        chat_links_response = extract_list(chat_links_response)

        # Update token count
        web_scraper_obj.increase_input_tokens(input_tokens)
        web_scraper_obj.increase_output_tokens(output_tokens)
        
        print(f"Important Links: {chat_links_response}")

        # Use chat model to get the use cases
        chat_use_cases_obj = ChatGPT(model_name, prompts_obj.startup_summary(startup_name, page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_use_cases_response, input_tokens, output_tokens = chat_use_cases_obj.chat_model()
        # print(f"AI Use Cases: {chat_use_cases_response}")
        ai_use_cases.append(chat_use_cases_response)

        # Update token count
        web_scraper_obj.increase_input_tokens(input_tokens)
        web_scraper_obj.increase_output_tokens(output_tokens)

        # Update the startup use cases with the important links
        # Also return the updated token count
        all_ai_use_cases = traverse_links(web_scraper_obj, chat_links_response, model_name, ai_use_cases, prompts_obj)
        
        # Prompt based approach for the EU AI Act
        eu_ai_act_obj = ChatGPT(model_name, prompts_obj.eu_ai_act_prompt(all_ai_use_cases), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        eu_ai_act_response, input_tokens, output_tokens = eu_ai_act_obj.chat_model()
        print(f"EU AI Act Response: {eu_ai_act_response}")
        # Update token count
        web_scraper_obj.increase_input_tokens(input_tokens)
        web_scraper_obj.increase_output_tokens(output_tokens)


        save_to_excel(output_sheet, output_wb, startup_name, web_scraper_obj, chat_links_response, all_ai_use_cases, eu_ai_act_response)

        print(f"Finished processing startup: {startup_name}")
        web_scraper_obj.quit_driver()
        # time.sleep(100)

def traverse_links(web_scraper_obj, links, model_name, ai_use_cases, prompts_obj):
    # Traverse the important links
    for link in links:
        web_scraper_obj.set_url(link)
        print(f"Going into relavant link: {link}")
        web_scraper_obj.load_page()
        page_content = web_scraper_obj.get_page_content(model_name)
        print(f"Page Content from relavant link: {page_content}")

        chat_use_case_obj = ChatGPT(model_name, prompts_obj.update_startup_summary(f"\n\n".join(ai_use_cases), page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_use_case_response, input_tokens, output_tokens = chat_use_case_obj.chat_model()

        # Update token count
        web_scraper_obj.increase_input_tokens(input_tokens)
        web_scraper_obj.increase_output_tokens(output_tokens)
        
        ai_use_cases.append(chat_use_case_response)

    return ai_use_cases

# Extract Python-style list from a string
def extract_list(input_string):
    # Regular expression to match Python-style lists
    list_pattern = r"\[.*?\]"
    match = re.search(list_pattern, input_string)
    if match:
        # Convert the matched string to a Python list
        return ast.literal_eval(match.group())
    return None

def save_to_excel(output_sheet, output_wb, startup_name, web_scraper_obj, additional_urls, all_ai_use_cases, eu_ai_act_response):
    headers = ["Startup Name", "Homepage URL", "Additional URLs"] + [f"AI Use Case {i+1}" for i in range(TOTAL_USE_CASES)] + ["EU AI Act Risk Classification"] + ["Total Input Tokens", "Total Output Tokens"]
    # Write headers if not present
    print(output_sheet.max_row)
    if output_sheet.max_row == 1:
        for col_num, header in enumerate(headers, start=1):
            output_sheet.cell(row=1, column=col_num, value=header)

    # Ensure all_ai_use_cases is padded to match the maximum number of columns
    use_cases_padded = all_ai_use_cases + [""] * (TOTAL_USE_CASES - len(all_ai_use_cases))

    # Write data
    row = [startup_name, web_scraper_obj.get_url(), ", ".join(additional_urls)] + use_cases_padded[:TOTAL_USE_CASES] + [eu_ai_act_response] + [web_scraper_obj.get_total_input_tokens(), web_scraper_obj.get_total_output_tokens()]
    output_sheet.append(row)

    # Save the workbook
    output_wb.save("ai_use_cases.xlsx")







def create_embeddings(input_csv, output_path, embedding_model_name, embedding_encoding, max_tokens):
    # Create the ChatGPT object (embedding model general function is inside ChatGPT class)
    embedding_object = ChatGPT(embedding_model_name, "", [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    
    # get the embeddings
    input_dataframe = pd.read_csv(input_csv)
    embeddings_object = Embeddings(embedding_object, embedding_encoding, max_tokens)
    embeddings_dataframe = embeddings_object.get_embeddings(input_dataframe)

    # save the embeddings
    embeddings_dataframe.to_csv(output_path, index=False)
    print(f"Embeddings saved to {output_path}")


def extract_use_cases_from_response(use_cases_full_text):
    all_use_cases = []
    # Extract each AI use case from the full text
    text_extractor = TextExtractor(use_cases_full_text)
    text_extractor.set_use_cases()
    df_use_cases = text_extractor.get_use_cases()
    
    for index, row in df_use_cases.iterrows():
        row_string = "\n".join(f"{col}: {val}" for col, val in row.items())
        all_use_cases.append(row_string + '\n\n')
    
    return all_use_cases    


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))




def get_similarity(df_existing_embeddings, embedding_model_name, ai_use_case, n=3):
    # Get the embeddings for the AI use case
    embedding_object = ChatGPT(embedding_model_name, ai_use_case, [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    use_case_embeddings = embedding_object.embedding_model()

    # Compute similarities
    df_existing_embeddings["similarity"] = df_existing_embeddings.embedding.apply(
        lambda x: cosine_similarity(x, use_case_embeddings)
    )

    # Get top results
    results = df_existing_embeddings.sort_values("similarity", ascending=False).head(n)

    # Extract the Text column from the matched rows
    matched_texts = results['Text'].tolist()
    return matched_texts




def second_step_similarity():
    # Calculate similarity between the AI use cases and the AI Act text
    df = pd.read_excel("ai_use_cases.xlsx")
    # Get the last non-empty generated AI use case
    target_columns = ['AI Use Case 1', 'AI Use Case 2', 'AI Use Case 3', 'AI Use Case 4']
    ai_use_cases = df[target_columns].apply(lambda row: row.dropna().iloc[-1] if not row.dropna().empty else None, axis=1).to_numpy()

    # Extract the AI use cases from the full text
    all_use_cases = []
    for use_case in ai_use_cases:
        if use_case:
            all_use_cases.extend(extract_use_cases_from_response(use_case))

    # Load the embeddings for the AI Act text
    df_existing_embeddings = pd.read_csv("datasets/ai_act_with_embeddings.csv")
    df_existing_embeddings["embedding"] = df_existing_embeddings.embedding.apply(literal_eval).apply(np.array)


    df_similarities = pd.DataFrame(columns=['AI Use Case', 'Similarity'])
    similarity_rows = []
    # Get the similarity between the AI use case and the AI Act text
    for use_case in all_use_cases:
        specific_clause = get_similarity(df_existing_embeddings, "text-embedding-3-small", use_case, n=3)
        similarity_rows.append({"AI Use Case": use_case, "Similarity": specific_clause})

    df_similarities = pd.concat([df_similarities, pd.DataFrame(similarity_rows)], ignore_index=True)
    df_similarities.to_csv("similarity_results.csv", index=False)


if __name__ == "__main__":
    prompt_approach()

    # Create embeddings for the AI Act text
    # create_embeddings("datasets/ai_act.csv", "datasets/ai_act_with_embeddings.csv", "text-embedding-3-small", "cl100k_base", 8000)

    # second_step_similarity()

    # pass






