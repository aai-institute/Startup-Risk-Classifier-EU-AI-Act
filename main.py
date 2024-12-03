from Classes import ChatGPT, Prompts, WebScraper, Embeddings

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
    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    # sheet.max_row + 1
    for row in range(7, 12):
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




if __name__ == "__main__":
    # prompt_approach()
    pass