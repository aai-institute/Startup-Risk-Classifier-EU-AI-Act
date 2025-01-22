from Classes import ChatGPT, Prompts, WebScraper, TextExtractor

from openai import OpenAI
import re
import ast
import openpyxl

import os
from dotenv import load_dotenv
load_dotenv()

TOTAL_USE_CASES = 4

def prompt_approach():
    sheet = openpyxl.load_workbook("raw-dealroom.xlsx")["Sheet1"]
    model_name = "chatgpt-4o-latest"
    classification_model_name = "chatgpt-4o-latest"
    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    # web_scraper_obj = None

    # sheet.max_row + 1
    for row in range(2, 4):
        url = sheet.cell(row=row, column=4).value
        startup_name = sheet.cell(row=row, column=2).value

        # Initialize the objects
        web_scraper_obj = WebScraper(url)
        prompts_obj = Prompts(TOTAL_USE_CASES)
        ai_use_cases = []

        homepage_url = web_scraper_obj.get_url()
        print(f"URL: {web_scraper_obj.get_url()}")
        
        # Load page, get the content and links
        web_scraper_obj.load_page()
        page_content = web_scraper_obj.get_page_content(model_name)
        page_links = web_scraper_obj.get_page_links()


        # Use chat model to get relavant links
        chat_links_obj = ChatGPT(model_name, prompts_obj.get_important_links(page_links), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_links_response, input_tokens, output_tokens = chat_links_obj.chat_model()
        chat_links_response = extract_list(chat_links_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        
        print(f"Important Links: {chat_links_response}")

        # Use chat model to get the use cases
        chat_use_cases_obj = ChatGPT(model_name, prompts_obj.startup_summary(startup_name, page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_use_cases_response, input_tokens, output_tokens = chat_use_cases_obj.chat_model()
        # print(f"AI Use Cases: {chat_use_cases_response}")
        ai_use_cases.append(chat_use_cases_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)

        # Update the startup use cases with the important links
        # Also return the updated token count
        all_ai_use_cases = traverse_links(web_scraper_obj, chat_links_response, model_name, ai_use_cases, prompts_obj)

        # Prompt based approach for the EU AI Act
        eu_ai_act_obj = ChatGPT(classification_model_name, prompts_obj.eu_ai_act_prompt(all_ai_use_cases), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        eu_ai_act_response, input_tokens, output_tokens = eu_ai_act_obj.chat_model()
        print(f"EU AI Act Response: {eu_ai_act_response}")
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, classification_model_name)


        save_to_excel(output_sheet, output_wb, startup_name, homepage_url, web_scraper_obj, chat_links_response, all_ai_use_cases, eu_ai_act_response)

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

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        
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

def save_to_excel(output_sheet, output_wb, startup_name, homepage_url, web_scraper_obj, additional_urls, all_ai_use_cases, eu_ai_act_response):
    headers = ["Startup Name", "Homepage URL", "Additional URLs"] + [f"AI Use Case {i+1}" for i in range(TOTAL_USE_CASES)] + ["EU AI Act Risk Classification", "Total Token Cost ($)"]
    # Write headers if not present
    print(output_sheet.max_row)
    if output_sheet.max_row == 1:
        for col_num, header in enumerate(headers, start=1):
            output_sheet.cell(row=1, column=col_num, value=header)

    # Ensure all_ai_use_cases is padded to match the maximum number of columns
    use_cases_padded = all_ai_use_cases + [""] * (TOTAL_USE_CASES - len(all_ai_use_cases))

    # Write data
    row = [startup_name, homepage_url, ", ".join(additional_urls)] + use_cases_padded[:TOTAL_USE_CASES] + [eu_ai_act_response] + [web_scraper_obj.get_token_cost()]
    output_sheet.append(row)

    # Save the workbook
    output_wb.save("ai_use_cases.xlsx")




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


if __name__ == "__main__":
    prompt_approach()

    # pass






