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
    
    def eu_ai_act_prompt(self, all_use_cases):
        eu_ai_act = f"""
        You are an expert lawyer who is intimately familiar with the European Union's Artificial Intelligence (EU AI) Act. 

Please classify a given AI use case into the following categories based on the EU AI Act's risk classification rules: 

1) Prohibited  
2) High-risk  
3) Systems with transparency obligations  
4) Low-risk

During this analysis, do not hallucinate facts, do not make the classification based on your assumptions about these risk classes, and rely only on the information provided in the prompts. 

Please perform this classification in the following manner: 


Step 1: Check if the AI Use Case is high-risk based on the following information:

'''
To help determine if the AI Use Case is classified as high-risk under the EU AI Act, please analyze the following information:

1\. Product/Component Assessment:

First, understand if the system is a "safety component":: 

A component is considered a "safety component" if EITHER:   
\- It fulfills a safety function for a product or system OR   
\- Its failure or malfunctioning endangers the health and safety of persons 

Examples of safety components:   
\- Systems monitoring water pressure in critical infrastructure   
\- Fire alarm controlling systems in computing centers   
\- Components that directly protect physical integrity of infrastructure   
\- Components that protect health and safety of persons and property 

Note: Components used solely for cybersecurity purposes are NOT considered safety components.

Then, check if the AI system is a product, or safety component of a product, covered by any of these Union harmonization laws under Annex I of the AI Act:

Section A (New Legislative Framework): 

* Machinery Directive (2006/42/EC)   
* Toy Safety Directive (2009/48/EC)   
* Recreational Craft Directive (2013/53/EU)   
* Lifts Directive (2014/33/EU)   
* ATEX Directive (2014/34/EU) \- Equipment for explosive atmospheres   
* Radio Equipment Directive (2014/53/EU)   
* Pressure Equipment Directive (2014/68/EU)   
* Cableway Installations Regulation (2016/424)   
* Personal Protective Equipment Regulation (2016/425)   
* Gas Appliances Regulation (2016/426)   
* Medical Devices Regulation (2017/745)   
* In Vitro Diagnostic Medical Devices Regulation (2017/746) 

Section B: 

* Civil Aviation Security Regulation (300/2008)   
* Two/Three-Wheel Vehicles Regulation (168/2013)   
* Agricultural/Forestry Vehicles Regulation (167/2013)   
*  Marine Equipment Directive (2014/90/EU)   
* Rail System Interoperability Directive (2016/797)   
* Motor Vehicles Regulation (2018/858)   
* Civil Aviation/EASA Regulation (2018/1139) 

2\. Standalone System Assessment:  
Does the system's purpose align with any of these areas in Annex III of the AI Act:

a) Biometric Identification & Categorization:  
\- Remote biometric identification systems  
\- Biometric categorization systems based on sensitive attributes  
\- Emotion recognition systems  
(Note: Excludes 1:1 verification/authentication systems)

b) Critical Infrastructure:  
\- Safety components in management/operation of critical digital infrastructure  
\- Safety components in road traffic, water/gas/heating/electricity supply  
(Note: Excludes cybersecurity-only systems)

c) Education/Training:  
\- Systems for determining access/admission  
\- Systems for evaluating learning outcomes  
\- Systems for assessing education levels  
\- Systems for monitoring student behavior during tests

d) Employment/Worker Management:  
\- Recruitment and selection systems  
\- Systems for promotion/termination decisions  
\- Task allocation systems  
\- Performance monitoring systems

e) Essential Services Access:  
\- Public assistance benefit evaluation systems  
\- Creditworthiness assessment systems  
\- Life/health insurance risk assessment systems  
\- Emergency service dispatch/prioritization systems

f) Law Enforcement:  
\- Risk assessment systems (victim/offender)  
\- Lie detection/similar tools  
\- Evidence reliability evaluation  
\- Criminal profiling systems  
\- Natural person profiling systems

g) Migration/Asylum/Border Control:  
\- Lie detection tools  
\- Risk assessment systems  
\- Document/evidence verification systems  
\- Border monitoring/surveillance systems

h) Justice/Democratic Processes:  
\- Systems assisting judicial decisions  
\- Systems influencing voting behavior/election outcomes  
(Note: Excludes administrative campaign management tools)

3\. Exception Analysis:  
If the system falls under an Annex III area, could it qualify for any exceptions:

a) Narrow Procedural Task:  
\- Does it only transform data formats?  
\- Does it only classify/categorize documents?  
\- Does it only detect duplicates?

b) Improvement of Human Activity:  
\- Does it only enhance previously completed work?  
\- Does it only provide an additional layer to human activity?  
\- Example: Improving language in drafted documents

c) Pattern Detection:  
\- Does it only identify patterns in previous decisions?  
\- Is it used only for ex-post analysis?  
\- Does it require human review?  
\- Example: Analyzing grading patterns for inconsistencies

d) Preparatory Tasks:  
\- Is it limited to file handling/indexing?  
\- Does it only process/link data?  
\- Is it only used for translation?

Important: These exceptions do not apply if the system performs profiling of natural persons.  
'''



Step 2: Check if additional transparency obligations apply to the AI Use Case based on the following information  

'''  
To help determine if the AI Use Case is classified as having transparency obligations under the EU AI Act, please analyze the following information:

Key Categories Requiring Transparency:

1. Systems Interacting with Natural Persons (Art 50(1))  
* Applies when there's a risk that people might believe they're interacting with a human  
* Exception: When it's obvious from the circumstances/context  
* Exception: Law enforcement systems for detecting/preventing crime  
* Example: AI chatbots, virtual assistants

2. Systems Generating Synthetic Content (Art 50(2))  
* Covers AI systems generating audio, image, video, or text content  
* Exception: Systems only performing assistive function for standard editing  
* Exception: Systems not substantially altering input data  
* Example: Image generators, text-to-speech systems

3. Emotion Recognition Systems (Art 50(3))  
* Systems identifying/inferring emotions or intentions based on biometric data  
* Example: Systems analyzing facial expressions for emotional states

4. Biometric Categorization Systems (Art 50(3))  
* Systems categorizing people based on biometric data  
* Example: Systems categorizing people by age, gender, or other characteristics

5. Deep Fakes/Manipulated Content (Art 50(4))  
* Content resembling existing persons/places that appears authentic  
* Exception: Creative/artistic/satirical content (requires different disclosure approach)  
* Exception: AI-generated text that undergoes human review/editorial control  
* Example: AI-generated videos of real people

'''

If you believe transparency obligations apply, please do the following:

- If the system was also high-risk based on the previous step, please return: “high-risk and transparency obligations”  
- Terminate the analysis here

If you believe transparency obligations *do not apply* or are unsure: 

- Return “low-risk”



Format you answer in this way:

AI Use Case: 
Use Case Description: 
Risk Classification: 
Reason: [Cite relevant annexes and clauses from the instructions above in your reasoning]
Requires Additional Information: [If you have doubts about this classification, answer 'Yes' or 'No', followed by what additional informtaion was necessary to classify this use case]

Do not give any intros or outros. The following are the AI Use cases of the startup you have to classify using all of the above rules:  
{all_use_cases}
        """

        # print(eu_ai_act)
        # eu_ai_act_without_prompt = f"For each of the following AI use cases, classify them according to the EU AI Act. Format you answer in this way:\n\nAI Use Case:\nContextual Considerations:\nRisk Classification:\nReason:\n\n{all_use_cases}"
        # print(eu_ai_act_without_prompt)
        return eu_ai_act




# Requires Additional Information: [If you have doubts about this classification, write 'Yes or No' followed by what additional informtaion is absolutely necessary without which you can't be sure about the classification]