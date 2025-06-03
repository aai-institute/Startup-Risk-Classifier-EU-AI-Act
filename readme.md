# Risk Classification of AI startups according to the EU AI Act

## Description
The repo is a Python implementation of an AI agent that generates AI use cases of startups and generates risk classifications for each use case according to the EU AI Act.

## Features

- **Collection of Use Cases:** Uses GPT Web Search API to collect AI startup use cases.
- **Risk Classification:** Uses model ensembling with 5 state-of-the-art-llms: ChatGPT 4o
  - ChatGPT 4o  
  - Claude 3.7 Sonnet  
  - DeepSeek Reasoner  
  - Gemini 2.0 Flash Thinker  
  - Mistral Large  

## Method

The approach is **Explainable zero-shot classification**. A classification prompt is used to generate the risk classifications. The ensembling method produces 5 classifications for each use case. A voter mechanism is then used to pick the classification with the highest number of votes.

## Quick Usage: 
```bash
python ./main.py
```

## Other Features:
- A sample input is included at `datasets\Use Cases\example_use_cases.json`
- To generate new AI use cases, use the `gpt_search` function in `main.py`

