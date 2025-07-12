# Standard Library
import os
import re
import ast
import json
import time
import csv
import argparse
# Third-Party Library
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import urllib

# Local Imports
from Classes import ChatGPT, Prompts, WebScraper
from large_prompts.master_prompt import master_prompt
from re_functions.use_case_extractor import extract_use_cases
from simple_model_functions.api_functions import gemini_api, mistral_api


# Load environment variables
load_dotenv()

# Constants
TOTAL_PAGE_CRAWLS = 4


def claude_api(model, prompt):
    try:
        client = anthropic.Anthropic(
            api_key=os.getenv("MY_ANTHROPIC_KEY")
        )
        message = client.messages.create(
            model=model,
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        message_content = message.content[0].text  # Extracts the actual message text
        input_tokens = message.usage.input_tokens  # Extracts input tokens
        output_tokens = message.usage.output_tokens  # Extracts output tokens

    except Exception as e:
        message_content = f"API ERROR: Anthropic API failed"
        input_tokens = 0
        output_tokens = 0

    return message_content, input_tokens, output_tokens

def claude_search(web_search_model, url, web_scraper_obj):
    client = anthropic.Anthropic(api_key=os.getenv("MY_ANTHROPIC_KEY"))

    response = client.messages.create(
        model=web_search_model,
        max_tokens=12000,
        messages=[
            {
                "role": "user",
                "content": f"""Identify and list the top 5 AI use cases, AI systems, or artificial intelligence applications on {url} as individual entries (provide fewer if less than 5 exist). For each distinct AI system (treat each AI module, tool, or application as separate even if part of the same platform), provide comprehensive details including:
- What specific data is collected and processed (including biometric, personal, behavioral data)
- How automated decisions are made and what decisions the AI makes
- Level of human oversight (fully automated vs human-in-the-loop vs human review)
- Who is directly affected by the AI system's outputs and decisions
- Specific business impact and consequences of the AI's decisions
- Technical implementation details about functionality, scope, and processing methods
- Whether users/affected parties are informed about AI usage
- Any compliance, privacy, or safety measures mentioned

Present each AI system as a separate, standalone use case with its own complete description, even if they're components of a larger platform. Start each use case with ###### followed by the use case name."""
            }
        ],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
            "allowed_domains": [f"{url}"],

            "user_location": {
                "type": "approximate",
                "city": "Berlin",
                "region": "Berlin",
                "country": "DE",
                "timezone": "Europe/Berlin"
            }
        }]
    )


    # Extract final answer text from response
    text_blocks = [block.text for block in response.content if block.type == 'text' and block.text]
    full_answer = ''.join(text_blocks)

    return full_answer

def call_model_with_retry(model_name, model_type, formatted_prompt, web_scraper_obj, max_retries=4, retry_delay=10):
    """
    Generic function to call any model with retry logic
    """
    for attempt in range(max_retries):
        try:
            if model_type == "chatgpt":
                chat_obj = ChatGPT(model_name, formatted_prompt, [], OpenAI(api_key=os.getenv("MY_1_KEY"), max_retries=5))
                response, input_tokens, output_tokens = chat_obj.chat_model()
            elif model_type == "claude":
                response, input_tokens, output_tokens = claude_api(model_name, formatted_prompt)
            elif model_type == "deepseek":
                chat_obj = ChatGPT(model_name, formatted_prompt, [], OpenAI(api_key=os.getenv("DEEPSEEK_KEY"), max_retries=5, base_url="https://api.deepseek.com"))
                response, input_tokens, output_tokens = chat_obj.chat_model()
            elif model_type == "gemini":
                response, input_tokens, output_tokens = gemini_api(model_name, formatted_prompt)
            elif model_type == "mistral":
                response, input_tokens, output_tokens = mistral_api(model_name, formatted_prompt)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
            response += "\n\n########END OF USE CASE########\n\n"
            return response
            
        except Exception as e:
            print(f"Error in {model_type.upper()} API call. Attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                web_scraper_obj.set_token_cost(input_tokens=0, output_tokens=0, model_name=model_name)
                raise RuntimeError(f"{model_type.upper()} Classification failed") from e


def use_case_separator(all_use_cases):
    # Find all headings that mark new use cases (e.g., "###### Use Case Name")
    sections = re.split(r'\n###### (.+)', all_use_cases)

    # Organize the extracted parts into a dictionary
    use_cases = {}
    for i in range(1, len(sections), 2):
        name = sections[i].strip()
        content = sections[i + 1].strip()
        use_cases[name] = content

    # for name, content in use_cases.items():
    #     print(f"--- Use Case: {name} ---\n{content}\n\n\n\n\n\n")

    return use_cases


def run_search_workflow(input_file, output_file):
    """
    Process URLs from a CSV file using claude_search and output results to a new CSV file
    """
    web_search_model = "claude-3-7-sonnet-20250219"
    
    try:
        # Initialize WebScraper for token cost tracking
        web_scraper_obj = WebScraper()
        
        # Initialize output CSV file
        with open(output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Company Name", "Use Case Name", "Use Case Description"])
        
        # Read input CSV file
        with open(input_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row_idx, row in enumerate(reader):
                company_name = row.get("Company Name", "")
                url = row.get("URLs", "") or row.get("URL", "")
                
                # If no company name provided, try to extract from URL
                if not company_name and url:
                    parsed_url = urllib.parse.urlparse(url)
                    domain = parsed_url.netloc
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        company_name = domain_parts[-2].capitalize()
                
                if not url:
                    continue
                
                # Extract domain from URL
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    domain = '.'.join(domain_parts[-2:])
                
                if domain:
                    print(f"Processing URL {row_idx + 1}: {domain} (Company: {company_name})")
                    
                    try:
                        # Perform search
                        search_result = claude_search(web_search_model, domain, web_scraper_obj)
                        
                        # Use the use_case_separator function to break down the use cases
                        use_cases_dict = use_case_separator(search_result)
                        
                        print(f"Found {len(use_cases_dict)} use cases for {company_name}")
                        
                        # Append results to CSV file
                        with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            if use_cases_dict:
                                for use_case_name, use_case_description in use_cases_dict.items():
                                    writer.writerow([company_name, use_case_name, use_case_description])
                            else:
                                # If no use cases found, create a single row with an error message
                                writer.writerow([company_name, "No structured use cases found", "No use cases found in the search result."])
                        
                        print(f"Successfully processed: {url}")
                        
                    except Exception as e:
                        print(f"Error processing {url}: {str(e)}")
                        # Append error row to CSV
                        with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow([company_name, "Error", f"Error: {str(e)}"])
        
        print(f"Search results saved to CSV: {output_file}")
        print(f"Total token cost: ${web_scraper_obj.get_token_cost():.4f}")
        
    except Exception as e:
        print(f"Error in search workflow: {str(e)}")
        raise


def classify_from_csv(input_csv, output_csv, models):
    """
    Read use cases from a CSV file and classify them one by one, saving results to CSV
    """
    # Model configurations with hardcoded model names
    all_model_configs = {
        "chatgpt": ("chatgpt-4o-latest", "chatgpt", "ChatGPT 4o"),
        "claude": ("claude-3-7-sonnet-20250219", "claude", "Claude 3.7 Sonnet"),
        "deepseek": ("deepseek-reasoner", "deepseek", "DeepSeek Reasoner"),
        "gemini": ("gemini-2.0-flash-thinking-exp-01-21", "gemini", "Gemini 2.0 Flash Thinker"),
        "mistral": ("mistral-large-latest", "mistral", "Mistral Large")
    }
    
    # Filter model configurations based on user selection
    model_configs = [all_model_configs[model] for model in models if model in all_model_configs]
    
    if not model_configs:
        raise ValueError("No valid models specified")
    
    print(f"Using {len(model_configs)} models: {[config[2] for config in model_configs]}")
    
    # Allowed categories
    allowed_categories = [
        'Prohibited AI system',
        'High-risk AI system under Annex I',
        'High-risk AI system under Annex III',
        'High-risk AI system with transparency obligations',
        'System with transparency obligations',
        'Low-risk AI system',
        'Uncertain'
    ]

    # Initialize the objects
    web_scraper_obj = WebScraper()
    prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)

    MAX_API_TRIES = 4
    retry_delay = 10

    # Initialize output CSV file
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company Name", "Use Case Name", "Use Case Description", "Risk Classification", "Reason", "Model Distribution", "Chosen Model", "Token Cost ($)"])

    # Read input CSV file
    with open(input_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row_idx, row in enumerate(reader):
            company_name = row.get("Company Name", "")
            use_case_name = row.get("Use Case Name", "")
            use_case_description = row.get("Use Case Description", "")
            
            print(f"Processing row {row_idx + 1}: {company_name} - {use_case_name}")
            
            # Create use case object for processing
            use_case = {
                "use_case_name": use_case_name,
                "use_case_description": use_case_description
            }
            
            use_case_string = f"AI Use Case: {use_case_name}\nUse Case Description: {use_case_description}"
            
            # Prepare the prompt with the use case
            formatted_prompt = prompts_obj.prepare_AI_Act_prompt(master_prompt, use_case_string)
            
            # Call all models and collect responses
            model_responses = []
            for model_name, model_type, display_name in model_configs:
                try:
                    response = call_model_with_retry(model_name, model_type, formatted_prompt, web_scraper_obj, MAX_API_TRIES, retry_delay)
                    model_responses.append(response)
                except Exception as e:
                    print(f"Error with {display_name}: {str(e)}")
                    model_responses.append(f"Error: {str(e)}")

            # Combine all responses
            final_string = "".join(model_responses)

            # Get the combined json from all models
            result_json = extract_use_cases(use_case, final_string)

            # Create a dictionary to store the votes and store individual classifications from all models
            voters = [config[2] for config in model_configs]
            votings = {}
            classifications_list = []
            
            # Iterate through the result JSON and count votes for each classification
            for model_use_case in result_json:
                classification = model_use_case["Risk Classification"]
                if classification in allowed_categories:
                    if classification not in votings:
                        votings[classification] = 0
                    votings[classification] += 1
                    classifications_list.append(classification)
                else:
                    # If the classification is not in the allowed categories, re-classify it as "Uncertain"
                    model_use_case["Risk Classification"] = "Uncertain"
                    classifications_list.append("Uncertain")
                    if "Uncertain" not in votings:
                        votings["Uncertain"] = 0
                    votings["Uncertain"] += 1

            # Find the classification with the most votes
            max_votes = max(votings.values())
            classifications_with_max_votes = [classification for classification, votes in votings.items() if votes == max_votes]
            
            # If tie, pick least risky from the tie group
            if len(classifications_with_max_votes) > 1:
                classifications_with_max_votes.sort(
                    key=lambda x: allowed_categories.index(x) if x in allowed_categories else -1,
                    reverse=True
                )
            final_classification = classifications_with_max_votes[0]

            print(f"Final Classification: {final_classification}")

            # Store the vote distribution from each model
            model_distribution = dict(zip(voters, classifications_list))
            model_distribution_string = ""
            for model, classification in model_distribution.items():
                model_distribution_string += f"{model}: {classification}\n"

            # Get the use cases with the final classification
            filtered_use_cases = [model_use_case for model_use_case in result_json if model_use_case["Risk Classification"] == final_classification]
            
            # Get the use case with the longest reason
            longest_reasoned_use_case = max(filtered_use_cases, key=lambda x: len(x["Reason"]))
            longest_reasoned_use_case_index = result_json.index(longest_reasoned_use_case)
            chosen_model = voters[longest_reasoned_use_case_index]

            # Get token cost for this classification
            token_cost = web_scraper_obj.get_token_cost()

            # Write result to CSV immediately
            with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    company_name,
                    use_case_name,
                    use_case_description,
                    final_classification,
                    longest_reasoned_use_case["Reason"],
                    model_distribution_string.strip(),
                    chosen_model,
                    token_cost
                ])
            
            # Reset token cost for next iteration
            web_scraper_obj.reset_token_cost()

    print(f"Classification complete. Results saved to: {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="EU AI Act Risk Classification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py search -i companies.csv -o use_cases.csv
  python main.py classify -i use_cases.csv -o classifications.csv
  python main.py classify -i use_cases.csv -o classifications.csv -m chatgpt claude

Input CSV Formats:
  Search:   Company Name, URLs (or URL)
  Classify: Company Name, Use Case Name, Use Case Description

Available Models: chatgpt, claude, deepseek, gemini, mistral
""")
    
    parser.add_argument("command", choices=["search", "classify"], 
                       help="Command to run: 'search' for URL searching or 'classify' for risk classification")
    
    # Search and classify command arguments
    parser.add_argument("--input-file", "-i", type=str, required=True,
                       help="Input CSV file path")
    parser.add_argument("--output-file", "-o", type=str, required=True,
                       help="Output CSV file path")
    
    # Classification command arguments
    parser.add_argument("--models", "-m", type=str, nargs='+', 
                       choices=["chatgpt", "claude", "deepseek", "gemini", "mistral"],
                       default=["chatgpt", "claude", "deepseek", "gemini", "mistral"],
                       metavar="MODEL",
                       help="Select one or more models for classification (default: all models)")
    
    args = parser.parse_args()
    
    if args.command == "search":
        print(f"Running search workflow...")
        print(f"Input CSV: {args.input_file}")
        print(f"Output CSV: {args.output_file}")
        
        run_search_workflow(args.input_file, args.output_file)
        
    elif args.command == "classify":
        print(f"Running classification workflow...")
        print(f"Input CSV: {args.input_file}")
        print(f"Output CSV: {args.output_file}")
        print(f"Using models: {', '.join(args.models)}")
        
        classify_from_csv(
            input_csv=args.input_file,
            output_csv=args.output_file,
            models=args.models
        )


if __name__ == "__main__":
    main()



