# Standard Library
import os
import re
import time
import uuid
import ast

# Third-Party Library
import pandas as pd
import openpyxl
from docx import Document
from dotenv import load_dotenv
from openai import OpenAI

from flask import Flask, render_template,copy_current_request_context, request, jsonify, Response, send_file, session
from flask_socketio import SocketIO
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField

from werkzeug.utils import secure_filename
import redis

# Local Imports
from Classes import ChatGPT, Prompts, WebScraper, TextExtractor

# Load environment variables
load_dotenv()

# Constants
TOTAL_PAGE_CRAWLS = 4


def load_startups_excel(startups_file):
    sheet = openpyxl.load_workbook(startups_file)["Sheet1"]
    return sheet

def create_results_file():    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    return output_sheet, output_wb

def content_shortener(content_shortener_model, prompts_obj, page_content):
    chat_shorten_page_obj = ChatGPT(content_shortener_model, prompts_obj.shorten_page_content(page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    chat_shorten_page_response, input_tokens, output_tokens = chat_shorten_page_obj.chat_model()
    # print(f"Shortened Page Content: {chat_shorten_page_response}")

    return chat_shorten_page_response, input_tokens, output_tokens

def read_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs]) 
    return text

def prepare_AI_Act_prompt(prompt_file, all_ai_use_cases):

    # Read the Word document properly
    file_content = read_docx(prompt_file)

    file_content += f"""Format you answer in this way:

AI Use Case: 
Use Case Description: 
Risk Classification: <Do not use uncertain terms like "potentially" or "unsure". Always make a definitive classification. Make sure you have read the Annexes again.>
Reason: <Provide a justification based on the relevant annexes and clauses from the instructions above. Clearly explain why the use case falls under the chosen classification.>
Requires Additional Information: <Answer "Yes" or "No". If "Yes" specify exactly what additional information was needed to classify this use case.>

Do not include any intros or outros. The following are the AI Use cases of the startup you have to classify: {all_ai_use_cases}
"""

# Requires Additional Information: <If you have doubts about this classification, answer 'Yes' or 'No', followed by what additional informtaion was necessary to classify this use case>

    # print(file_content)  # Output all content
    return file_content



def prompt_approach(model_name, classification_model_name, content_shortener_model, sheet, output_sheet, output_wb, prompt_file, output_filename):
    # Initialize the objects
    web_scraper_obj = WebScraper()

    # sheet.max_row + 1
    for row in range(2, 11):
        url = sheet.cell(row=row, column=2).value
        startup_name = sheet.cell(row=row, column=1).value
        
        if pd.isnull(url):
            continue

        prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)
        ai_use_cases = []

        # First set the URL (this cleans the URL), then get the cleaned URL
        web_scraper_obj.set_url(url)
        raw_homepage_url = web_scraper_obj.get_url()
        # print(f"URL: {web_scraper_obj.get_url()}")
        time.sleep(1)
        yield f"data: Row {row}: {startup_name}\n\n"
        
        # Load page, get the content and links
        web_scraper_obj.load_page()

        # Get the content and links
        page_content = web_scraper_obj.get_page_content(model_name)
        page_links = web_scraper_obj.get_page_links()



        # Use chat model to get relavant links
        chat_links_obj = ChatGPT(model_name, prompts_obj.get_important_links(page_links), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_links_response, input_tokens, output_tokens = chat_links_obj.chat_model()
        chat_links_response = extract_list(chat_links_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        
        print(f"Important Links: {chat_links_response}")

        # Use a smaller model to remove cookie and unrelated text - reduces chance of classification error
        shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        # print(f"Shortened Content: {shortened_content}")


        # Use chat model to get the use cases
        chat_use_cases_obj = ChatGPT(model_name, prompts_obj.startup_summary(startup_name, shortened_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_use_cases_response, input_tokens, output_tokens = chat_use_cases_obj.chat_model()
        # print(f"AI Use Cases: {chat_use_cases_response}")
        ai_use_cases.append(chat_use_cases_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)

        # Update the startup use cases with the important links
        # Also return the updated token count
        all_ai_use_cases = traverse_links(web_scraper_obj, chat_links_response, model_name, content_shortener_model, ai_use_cases, prompts_obj)

        # Prompt based approach for the EU AI Act
        eu_ai_act_prompt = prepare_AI_Act_prompt(prompt_file, all_ai_use_cases)
        eu_ai_act_obj = ChatGPT(classification_model_name, eu_ai_act_prompt, [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        eu_ai_act_response, input_tokens, output_tokens = eu_ai_act_obj.chat_model()
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, classification_model_name)


        # Parse the highest risk classification
        risk_parse_obj = ChatGPT("gpt-4o", prompts_obj.get_highest_risk(eu_ai_act_response), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        risk_parse_response, input_tokens, output_tokens = risk_parse_obj.risk_classification_structured_chat()
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, "gpt-4o")

        risk_parse_response = json.loads(risk_parse_response)
        highest_risk_classification = risk_parse_response["highest_risk_classification"]
        requires_additional_information = risk_parse_response["requires_additional_information"]
        what_additional_information = risk_parse_response["what_additional_information"]


        save_to_excel(output_sheet, output_wb, startup_name, raw_homepage_url, web_scraper_obj, chat_links_response, all_ai_use_cases, eu_ai_act_response, highest_risk_classification, requires_additional_information, what_additional_information, output_filename)

        # --- Finishing calls ---
        # Reset token cost, redirected URL
        web_scraper_obj.reset_token_cost()
        web_scraper_obj.reset_redirect_url()


def traverse_links(web_scraper_obj, links, model_name, content_shortener_model, ai_use_cases, prompts_obj):
    # Traverse the important links
    for link in links:
        web_scraper_obj.set_url(link)
        # print(f"Going into relavant link: {link}")
        web_scraper_obj.load_page()
        page_content = web_scraper_obj.get_page_content(model_name)

        # Shorten the content
        shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)


        chat_use_case_obj = ChatGPT(model_name, prompts_obj.update_startup_summary(f"\n\n".join(ai_use_cases), shortened_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
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
        return ast.literal_eval(match.group())
    return None

def save_to_excel(output_sheet, output_wb, startup_name, raw_homepage_url, web_scraper_obj, additional_urls, all_ai_use_cases, eu_ai_act_response, highest_risk_classification, requires_additional_information, what_additional_information, output_filename):
    headers = ["Startup Name", "Homepage URL", "Redirected URL (for logging only)", "Additional URLs"] + [f"Page {i+1}" for i in range(TOTAL_PAGE_CRAWLS)] + ["EU AI Act Risk Classification", "Highest Risk Classification", "Requires Additional Information", "What Additional Information", "Total Token Cost ($)"]
    # Write headers if not present
    if output_sheet.max_row < 2:
        output_sheet.append(headers)

    # Ensure all_ai_use_cases is padded to match the maximum number of columns
    use_cases_padded = all_ai_use_cases + [""] * (TOTAL_PAGE_CRAWLS - len(all_ai_use_cases))

    # Write data
    row = [startup_name, raw_homepage_url, web_scraper_obj.get_redirected_url(), ", ".join(additional_urls)] + use_cases_padded[:TOTAL_PAGE_CRAWLS] + [eu_ai_act_response, highest_risk_classification, requires_additional_information, what_additional_information, web_scraper_obj.get_token_cost()]
    output_sheet.append(row)


    output_wb.save(f"user_downloads/{output_filename}")


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




app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'user_uploads'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'risk_classification:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, password=os.getenv('REDIS_PASSWORD'), decode_responses=False)
app.config['WTF_CSRF_ENABLED'] = True



Session(app)

ALLOWED_EXTENSIONS = {
    "file1": {"xlsx"},
    "file2": {"docx"}
}

class UploadFileForm(FlaskForm):
    file1 = FileField('Excel File (.xlsx only)')
    file2 = FileField('Word File (.docx only)')
    submit = SubmitField('Upload Files')

def allowed_file(filename, file_type):
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())


@app.route('/', methods=['GET'])
def index():
    form = UploadFileForm()
    return render_template('index.html', form=form)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Both files are required"}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    # Check if files are selected
    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Validate file types
    if not allowed_file(file1.filename, "file1"):
        return jsonify({"error": "File 1 must be an Excel (.xlsx) file"}), 400
    if not allowed_file(file2.filename, "file2"):
        return jsonify({"error": "File 2 must be a Word (.docx) file"}), 400

    # Generate a unique identifier for the file
    request_id = str(uuid.uuid4().hex)

    unique_filename1 = f"{request_id}_{secure_filename(file1.filename)}"
    unique_filename2 = f"{request_id}_{secure_filename(file2.filename)}"
    unique_filename3 = f"{request_id}.xlsx"

    upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)

    file1_path = os.path.join(upload_dir, unique_filename1)
    file2_path = os.path.join(upload_dir, unique_filename2)

    file1.save(file1_path)
    file2.save(file2_path)

    session[request_id] = {
        'startups_file': unique_filename1,
        'prompt_file': unique_filename2,
        'download_file': unique_filename3
    }

    # Send the unique identifier back to the client (for unique download link) 
    return jsonify({"message": "Files uploaded successfully!", "request_id": request_id})




def flask_web_scraper_runner(startups_file, prompt_file, output_filename):
    @copy_current_request_context  
    def process():
        yield f"data: Processing started. Each startup website will be scraped. Please wait...\n\n"
        time.sleep(1)

        sheet = load_startups_excel(f"user_uploads/{startups_file}")
        prompt_file_path = f"user_uploads/{prompt_file}"

        # Create the results file
        output_sheet, output_wb = create_results_file()

        yield from prompt_approach(model_name='chatgpt-4o-latest', classification_model_name='chatgpt-4o-latest', content_shortener_model='gpt-4o-mini', sheet=sheet, output_sheet=output_sheet, output_wb=output_wb, prompt_file=prompt_file_path, output_filename=output_filename)

        # Delete the uploaded files
        os.remove(f"user_uploads/{startups_file}")
        os.remove(f"user_uploads/{prompt_file}")

        yield "data: Processing complete!\n\n"
        
    return process()




@app.route('/run_process', methods=['GET'])
def run_process():
    request_id = request.args.get("request_id")
    
    if not request_id or request_id not in session:
        return jsonify({"error": "Session expired or files not uploaded"}), 400

    session_data = session[request_id]
    startups_file = session_data.get("startups_file")
    prompt_file = session_data.get("prompt_file")
    output_filename = session_data.get("download_file")

    if not startups_file or not prompt_file:
        return jsonify({"error": "Session expired or files not uploaded"}), 400


    return Response(flask_web_scraper_runner(startups_file, prompt_file, output_filename), mimetype='text/event-stream')


@app.route('/download')
def download_file():
    request_id = request.args.get("request_id")
    if not request_id or request_id not in session:
        return jsonify({"error": "No file available for download"}), 400

    filename = session[request_id].get('download_file')
    if not filename:
        return jsonify({"error": "No file available for download"}), 400

    file_path = os.path.join(os.getcwd(), f"user_downloads/{filename}")

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

import json

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

    # prompt_obj = Prompts(4)
    # prompt = prompt_obj.get_highest_risk(example_classifications)

    # chat_obj = ChatGPT("gpt-4o", prompt, [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    # response, input_tokens, output_tokens = chat_obj.risk_classification_structured_chat()
    # response = json.loads(response)


    




