from pydantic import BaseModel
from typing import List

class Risk_Classification_Structure(BaseModel):
    highest_risk_classification: str
    highest_risk_classification_use_case: str
    requires_additional_information: str
    what_additional_information: str

class Separate_Risks(BaseModel):
    prohibited_ai_system : List[str]
    high_risk_ai_system_under_annex_I : List[str]
    high_risk_ai_system_under_annex_III : List[str]
    system_with_transparency_obligations : List[str]
    high_risk_ai_system_with_transparency_obligations : List[str]
    low_risk_ai_system : List[str]
    unknown: List[str]


class ChatGPT():
    def __init__(self, model_name, prompt, context, client):
        self.__model_name = model_name
        self.__prompt = prompt
        self.__context = context
        self.__client = client
        # print(f"ChatGPT class initialized with model {self.__model_name}")

    def set_prompt(self, prompt):
        self.__prompt = prompt
    
    def chat_model(self):
        self.__context.append({"role": "user", "content": self.__prompt})

        try:
            response = self.__client.chat.completions.create(
                model=self.__model_name,
                messages=self.__context
            )

            answer = response.choices[0].message.content.strip()
            self.__context.append({"role": "assistant", "content": answer})

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            return [answer, input_tokens, output_tokens]
        
        except Exception as e:
            print(f"API Error: {e}")
            return [None, None]


    def chat_structured(self, task):
        self.__context.append({"role": "user", "content": self.__prompt})
        if task == "risk_classification":
            response_format = Risk_Classification_Structure
        elif task == "separate_risks":
            response_format = Separate_Risks

        try:
            response = self.__client.beta.chat.completions.parse(
                model=self.__model_name,
                messages=self.__context,
                response_format=response_format,
            )

            answer = response.choices[0].message.content.strip()
            self.__context.append({"role": "assistant", "content": answer})

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            return [answer, input_tokens, output_tokens]
        
        except Exception as e:
            print(f"API Error: {e}")
            return [None, None]
