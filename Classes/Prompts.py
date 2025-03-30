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


    # check Geoinsight.ai.
    def fix_raw_use_cases(self, raw_use_cases):
        fixed_use_cases = f"Rewrite all the following text. Make sure there are no stylings or numbered headings or any type of formattings such as but not limited to # or * or - etc. If the content is inside an array, convert it to plain text. All text must in paragraph style only. Remove all url citations if found. There should only be two sections in the output for each use case, 'AI Use Case:' and 'Use Case Description:' If you see other sections, they must be part of the use case description. Start with the name of the company in each description if its available in the content. Each section must always be on a new line and each use case block must be separated by 4 new lines.\n\n\n\n{raw_use_cases}"
        
        return fixed_use_cases
    
    def generate_use_case_gpt(self, url):
        generated_use_cases = f"{self.__use_english_prompt} Find out as much as you can about this company: {url} Give detailed AI use cases of this company. Leave out intros and outros, and focus only on AI use cases. Use the following format for each identified AI use case: AI Use Case: <name of the use case>\nUse Case Description: <detailed information about the use case>\n\n\nIn the description focus on these points: Intended purpose, Deployment context/sector, Level of autonomy, Impact on individuals, Types of data used, User type, Adaptivity/learning in deployment, Safety-critical nature of system. Use the information from the website and also use your own knowledge if you already know about the company. Always respond in plain text only without any markdown formatting like *, #, - etc. If you cannot find any information, respond with 'No information found' and no other text."
        
        return generated_use_cases
