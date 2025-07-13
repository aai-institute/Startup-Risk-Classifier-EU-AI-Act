# EU AI Act Risk Classification Tool - Usage Guide

## Overview
This tool provides two main functionalities:
1. **Search**: Extract AI use cases from websites using Claude's web search capabilities
2. **Classify**: Classify AI use cases from a CSV file using multiple AI models

## Command Line Usage

### Search Command
Extract AI use cases from websites listed in a CSV file and output structured use cases:

```bash
python main.py search --input-file sample_urls.csv --output-file search_results.csv
```

**Options:**
- `--input-file, -i`: Input CSV file with URLs column (required)
- `--output-file, -o`: Output CSV file for results (required)

**Note:** The search model is hardcoded to use `claude-sonnet-4-20250514` for consistency.

**Input CSV Format:**
The CSV file should have columns named "Company Name" and "URLs":

```csv
Company Name,URLs
OpenAI,https://openai.com
Anthropic,https://anthropic.com
Google AI,https://ai.google
```

**Output CSV Format:**
The output file will have the following structure:

```csv
Company Name,Use Case Name,Use Case Description
OpenAI,GPT-4,GPT-4 is a large multimodal model...
OpenAI,DALL-E 3,DALL-E 3 is an image generation model...
OpenAI,ChatGPT,ChatGPT is a conversational AI assistant...
```

**Key Features:**
- Automatically separates multiple use cases found for each company
- Creates multiple rows for each company if multiple use cases are found
- Output format matches the input format expected by the `classify` command
- Extracts company name from URL if not provided in input file

### Classify Command
Classify AI use cases from a CSV file:

```bash
python main.py classify --input-file sample_use_cases.csv --output-file classification_results.csv
```

**Options:**
- `--input-file, -i`: Input CSV file with use cases (required)
- `--output-file, -o`: Output CSV file for results (required)
- `--models, -m`: Models to use for classification (choices: chatgpt, claude, deepseek, gemini, mistral)

**Model Selection Examples:**
```bash
# Use Claude Sonnet 4 (default)
python main.py classify -i input.csv -o output.csv

# Use only ChatGPT and Claude
python main.py classify -i input.csv -o output.csv --models chatgpt claude

# Use only 3 models
python main.py classify -i input.csv -o output.csv -m chatgpt claude gemini
```

**Input CSV Format:**
The CSV file should have the following columns. They are the same as created by the `search` command.
- `Company Name`: Name of the company
- `Use Case Name`: Name of the AI use case
- `Use Case Description`: Detailed description of the AI use case

Example:
```csv
Company Name,Use Case Name,Use Case Description
TechCorp,AI Chatbot,Customer service chatbot that automatically responds to customer inquiries
DataInc,Predictive Analytics,Machine learning system that analyzes customer behavior patterns
```

**Output CSV Format:**
The output CSV will contain:
- `Company Name`: Original company name
- `Use Case Name`: Original use case name
- `Use Case Description`: Original use case description
- `Risk Classification`: EU AI Act risk classification
- `Reason`: Detailed reasoning for the classification
- `Model Distribution`: How each model voted
- `Chosen Model`: Which model's reasoning was selected
- `Token Cost ($)`: API cost of the classification

## EU AI Act Risk Classifications

The tool classifies AI systems into these categories:
- `Prohibited AI system`
- `High-risk AI system under Annex I`
- `High-risk AI system under Annex III`
- `High-risk AI system with transparency obligations`
- `System with transparency obligations`
- `Low-risk AI system`
- `Uncertain`

## Sample Files

### Sample CSV file for search (sample_urls.csv)
```csv
Company Name,URLs
OpenAI,https://openai.com
Anthropic,https://anthropic.com
Google AI,https://ai.google
```

### Sample CSV file for classification (sample_use_cases.csv)
```csv
Company Name,Use Case Name,Use Case Description
TechCorp,AI Chatbot,Customer service chatbot that automatically responds to customer inquiries and escalates complex issues to human agents
DataInc,Predictive Analytics,Machine learning system that analyzes customer behavior to predict purchasing patterns and recommend products
SecureAI,Facial Recognition,Biometric authentication system that uses facial recognition to grant access to secure facilities
```

## Environment Setup

Make sure you have the following environment variables set:
- `MY_ANTHROPIC_KEY`: Anthropic API key
- `MY_1_KEY`: OpenAI API key
- `DEEPSEEK_KEY`: DeepSeek API key
- `GEMINI_API_KEY`: Google Gemini API key
- `MISTRAL_API_KEY`: Mistral API key

## Examples

### Complete Search-to-Classification Workflow
```bash
# Step 1: Search for AI use cases from websites
python main.py search -i sample_urls.csv -o extracted_use_cases.csv

# Step 2: Classify the extracted use cases using all models
python main.py classify -i extracted_use_cases.csv -o final_classifications.csv
```

**Streamlined Workflow:**
```bash
# One-liner workflow using CSV files
python main.py search -i urls.csv -o use_cases.csv && python main.py classify -i use_cases.csv -o results.csv
```

### Custom Model Selection for Classification
```bash
# Use only ChatGPT and Claude models
python main.py classify -i use_cases.csv -o results.csv --models chatgpt claude

# Use only 3 specific models
python main.py classify -i use_cases.csv -o results.csv -m chatgpt deepseek gemini

# Use all models (default behavior)
python main.py classify -i use_cases.csv -o results.csv
```

### Quick Testing
```bash
# Test with sample files
python main.py search -i sample_urls.csv -o test_search_results.csv
python main.py classify -i sample_use_cases.csv -o test_classification_results.csv --models chatgpt claude
```
