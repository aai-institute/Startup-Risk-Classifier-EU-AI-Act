# EU AI Act Risk Classification Tool - Usage Guide

## Overview
This tool provides two main functionalities:
1. **Search**: Extract AI use cases from websites using Claude's web search capabilities
2. **Classify**: Classify AI use cases from a CSV file using multiple AI models

## Command Line Usage

### Search Command
Extract AI use cases from websites listed in a CSV file and output structured use cases:

```bash
python main.py search --input-file startups.csv --output-file use_cases.csv
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
python main.py classify --input-file use_cases.csv --output-file classifications.csv
```

**Options:**
- `--input-file, -i`: Input CSV file with use cases (required)
- `--output-file, -o`: Output CSV file for results (required)
- `--models, -m`: Models to use for classification (choices: chatgpt, claude, deepseek, gemini, mistral)

**Model Selection Examples:**
```bash
# Use Claude Sonnet 4 (default)
python main.py classify -i use_cases.csv -o classifications.csv

# Use Model Ensembling
python main.py classify -i use_cases.csv -o classifications.csv --models chatgpt claude gemini

# Use All Available Models
python main.py classify -i use_cases.csv -o classifications.csv -m chatgpt, claude, deepseek, gemini, mistral
```

**Input CSV Format:**
The CSV file should have the following columns. They are the same as created by the `search` command earlier.
- `Company Name`: Name of the company
- `Use Case Name`: Name of the AI use case
- `Use Case Description`: Detailed description of the AI use case

Example:
```csv
Company Name,Use Case Name,Use Case Description
OpenAI,GPT-4,GPT-4 is a large multimodal model...
OpenAI,DALL-E 3,DALL-E 3 is an image generation model...
OpenAI,ChatGPT,ChatGPT is a conversational AI assistant...
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

### Sample CSV file for search (startups.csv)
```csv
Company Name,URLs
OpenAI,https://openai.com
Anthropic,https://anthropic.com
Google AI,https://ai.google
```

## Environment Setup

Make sure you have the following environment variables set:
- `ANTHROPIC_KEY`: Anthropic API key
- `OpenAI_KEY`: OpenAI API key
- `DEEPSEEK_KEY`: DeepSeek API key
- `GEMINI_KEY`: Google Gemini API key
- `MISTRAL_KEY`: Mistral API key

## Examples

### Complete Search-to-Classification Workflow
```bash
# Step 1: Search for AI use cases from websites
python main.py search -i startups.csv -o use_cases.csv

# Step 2: Classify the extracted use cases using the default model (Claude Sonnet 4)
python main.py classify -i use_cases.csv -o classifications.csv
```

**Streamlined Workflow:**
```bash
# One-liner workflow using CSV files
python main.py search -i startups.csv -o use_cases.csv && python main.py classify -i use_cases.csv -o classifications.csv
```

## Acknowledgment
The Bavarian AI Act Accelerator is a two-year project funded by the Bavarian State Ministry of Digital Affairs to support SMEs, start-ups, and the public sector in Bavaria in complying with the EU AI Act. Under the leadership of the appliedAI Institute for Europe and in collaboration with Ludwig Maximilian University, the Technical University of Munich, and the Technical University of Nuremberg, training, resources, and events are being offered. The project objectives include reducing compliance costs, shortening the time to compliance, and strengthening AI innovation. To achieve these objectives, the project is divided into five work packages: project management, research, education, tools and infrastructure, and community.
