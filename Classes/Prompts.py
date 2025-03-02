class Prompts():
    def __init__(self, total_use_cases):
        self.__total_use_cases = total_use_cases
        self.__use_english_prompt = f"Respond in English.\n"
    
    def shorten_page_content(self, full_page_content):
        shortened_content = f"{self.__use_english_prompt} Remove any content from the following that doesn't directly describe the company's AI products, AI services or AI offerings. Mention the name of the company if its available in the content.\n Page Content: \n\n{full_page_content}"
        
        return shortened_content

    def startup_summary(self, startupName, raw_text):
        startup_summary = f"{self.__use_english_prompt} The following is the content of the homepage of a company's website whose supposed name is \"{startupName}\", but confirm this from the homepage content.\n\nYour task is to find all the AI use cases this company is implementing. Mention the AI process they use to implement that use case and the type of models they use. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing with AI or is currently under development. Format all the AI use cases in this format:\nAI Use Case: [name the use case here]\nUse Case Description:\nAI Process Used:\nType of Models Used:\n\nFocus only on the AI uses cases implemented by the company and leave out generic stuff about the company. If the content of this webpage is just a page error, then output 'Page Error' and then the reason. \n\nContent of the homepage: {raw_text}"

        return startup_summary

    def update_startup_summary(self, last_known_use_cases, page_content):
        update_summary = f"{self.__use_english_prompt} The following are the last known AI use cases I have for a company.\n\nYour task is to update and find all other AI use cases this company is implementing by using the content of a webpage of this company. Mention the AI process they use to implement that use case and the type of models they use. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing with AI or is currently under development. Format all the AI use cases in this format:\nAI Use Case: [name the use case here]\nUse Case Description:\nAI Process Used:\nType of Models Used:\n\nFocus only on the AI uses cases implemented by the company and leave out generic stuff about the company. If there is no valuable information in the content of the page, then just output all the last known AI use cases I have provided. If I also did not provide last known AI use cases, then output 'Page Error' and then the reason. \n\nLast known AI Uses Cases: {last_known_use_cases}.\n\nContent of the webpage: {page_content}"
        return update_summary

    def get_important_links(self, page_links):
        important_links = f"The following are all the links available on the homepage of a company's website. Use your best judgement to find a maximum of {self.__total_use_cases - 1} links which have the potential to describe more about the AI products or services offered by the company. This does not include pages that are similar to contact us, about us, pricing, impressum, privacy, terms-and-conditions or cookie related pages. Return only a list of links and no other text. If you can not find any relavant links, then return an empty list only.\n\nLinks: {page_links}"
        
        return important_links
    
    def combine_use_cases(self, all_ai_use_cases):
        combined_use_cases = f"The following are all the known AI use cases of a company. Make sure there are no duplicates and give them all again in the same format as they are given to you. If I do not provide the AI use cases, then output 'Error: No AI Use Cases Found'.\n\nAll AI Use Cases:\n\n {all_ai_use_cases}"
        
        return combined_use_cases
    
    def separate_risks(self, all_use_cases):
        separate_risks = f"""Read the following use cases: 

{all_use_cases}

Return **each** use case from above in the following strict **JSON** format and do not include any other text outside the JSON object. Each value should be an array of strings containing the **entire** respective use case. Put each section of a use case on a new line but there should be **no** empty lines in the use cases, and remove the bold (**) stars and other text formatting.

{{
    prohibited_ai_system:
    high_risk_ai_system_under_annex_I:
    high_risk_ai_system_under_annex_III:
    system_with_transparency_obligations:
    high_risk_ai_system_with_transparency_obligations:
    low_risk_ai_system:
    unknown:
}}
    """
        return separate_risks



    def get_highest_risk(self, all_use_cases):
        highest_risk = f"""What is the highest 'Risk Classification' mentioned in these risk classifications:

{all_use_cases}

The order of risk classification for this task from highest to lowest is:

1) Prohibited AI system
2) Unknown (if potentially high-risk but the classification is not clear)
2) High-risk AI system under Annex I
3) High-risk AI system under Annex III
4) System with transparency obligations
5) High-risk AI system with transparency obligations
6) Low-risk AI system

Identify the **highest risk classification** appearing in the text based on the ranking above. If there are multiple use cases with the same highest risk classification level, then choose the one that does not require additional information. If all of such use cases require additional information, then choose that appears first in the list.

Return the result in the following **strict JSON format** and **do not include any other text outside the JSON object**:

{{
  "highest_risk_classification": "<Extract the exact wording of the highest risk classification from the text>",
  "requires_additional_information": "<Yes or No>",
  "what_additional_information": "<If yes, what additional information is required for this use case. Otherwise, return an empty string>"
}}
"""

        return highest_risk
    

    



# Requires Additional Information: [If you have doubts about this classification, write 'Yes or No' followed by what additional informtaion is absolutely necessary without which you can't be sure about the classification]