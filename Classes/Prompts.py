class Prompts():
    def __init__(self, total_use_cases):
        self.__total_use_cases = total_use_cases
    
    def startup_summary(self, startupName, raw_text):
        startup_summary = f"The following is the content of the homepage of a company's website whose supposed name is \"{startupName}\", but confirm this from the homepage content.\n\nYour task is to generate all the AI use cases this company is implementing. Mention the AI process they use to implement that use case and the type of models they use. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing with AI. If the content of this webpage is just a page error, then output 'Page Error' only. \n\nContent of the homepage: {raw_text}"

        return startup_summary

    def update_startup_summary(self, last_known_use_cases, page_content):
        update_summary = f"The following are the last known AI use cases I have for a company.\n\nYour task is to update and find all other AI use cases this company is implementing by using the content of a webpage of this company. Mention the AI process they use to implement that use case and the type of models they use. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing. If there is no valuable information in the content of the page, then just output all the last known AI use cases I have provided. If I also did not provide last known AI use cases, then output 'Page Error' only. \n\nLast known AI Uses Cases: {last_known_use_cases}.\n\nContent of the webpage: {page_content}"
        return update_summary

    def get_important_links(self, page_links):
        important_links = f"The following are all the links available on the homepage of a company's website. Use your best judgement to determine a maximum of {self.__total_use_cases - 1} links which are most important to find all the AI use cases this company is implementing. Return only a list of links and no other text. If you can not find any relavant links, then return an empty list only.\n\nLinks: {page_links}"
        
        return important_links
    
    def eu_ai_act_prompt(self, all_use_cases):
        eu_ai_act = f"""You are an AI expert tasked with performing risk classification assessments for AI startups and their use cases according to the EU AI Act. Your goal is to categorize AI systems into the appropriate risk level based on the information provided. Here's how to conduct the assessment:
        Risk Categories
        Classify AI systems into one of four risk categories:
        Unacceptable Risk (Prohibited)
        High Risk
        Limited Risk
        Minimal Risk
        Category Definitions and Examples
        1. Unacceptable Risk (Prohibited)
        AI systems in this category are banned in the EU due to their potential threat to individuals and society. These include:
        Social scoring systems by governments
        AI manipulating vulnerable groups
        Real-time and remote biometric identification (e.g., facial recognition) in public spaces, except for specific law enforcement purposes with court approval
        AI systems using subliminal or manipulative techniques to distort behavior
        AI exploiting vulnerabilities related to age, disability, or socio-economic circumstances
        Biometric categorization systems inferring sensitive attributes (e.g., race, political opinions, religious beliefs, sexual orientation)
        AI for assessing an individual's risk of committing criminal offenses
        2. High Risk
        AI systems that could significantly impact safety, fundamental rights, or the environment. The following categories are to be considered high risk:

        Biometrics:
        Remote biometric identification systems (excluding verification of identity claims).
        Biometric categorization based on sensitive attributes.
        Emotion recognition systems.
        Critical Infrastructure:
        AI used as safety components in digital infrastructure, road traffic, or utilities (water, gas, heating, electricity).
        Education and Vocational Training:
        AI for admission or placement decisions.
        AI to evaluate learning outcomes or guide learning processes.
        AI assessing education access levels.
        AI monitoring prohibited behavior during tests.
        Employment and Workforce Management:
        AI for recruitment, filtering applications, or evaluating candidates.
        AI for decisions on work contracts, promotions, terminations, task allocations, or performance monitoring.
        Access to Essential Services:
        AI assessing eligibility for public benefits/services (e.g., healthcare).
        AI evaluating creditworthiness (excluding fraud detection).
        AI for risk assessment in life/health insurance pricing.
        AI classifying emergency calls or dispatching emergency services.
        Law Enforcement:
        AI assessing risk of victimization.
        AI as polygraphs or similar tools.
        AI evaluating evidence reliability.
        AI assessing reoffending risk (not solely based on profiling).
        AI for profiling during criminal investigations.
        Migration, Asylum, and Border Control:
        AI as polygraphs or similar tools.
        AI assessing security, migration, or health risks.
        AI for asylum, visa, or residence permit applications.
        AI for detecting or identifying persons in migration contexts (excluding travel document verification).
        Justice and Democratic Processes:
        AI assisting judicial authorities with legal interpretation or dispute resolution.
        AI influencing election/referendum outcomes or voting behavior (excluding backend campaign management tools).
        Common Examples:
        AI powered recruitment and development tools for human resources
        Legal AI assistants

        Note: An AI system listed in Annex III may not be considered high-risk if it meets certain conditions, such as improving previously completed human activity, or detecting decision-making patterns without replacing human assessment.
        3. Limited Risk
        AI systems with potential for manipulation or deceit, requiring transparency. General purpose AI (GPAI) models also fall under this category. 'General-purpose AI model' means an AI model trained on large-scale data, often using self-supervision, that exhibits broad versatility, can perform diverse tasks competently, and is integrable into various downstream systems or applications. This excludes models used solely for research, development, or prototyping prior to market placement.
        Systemic Risk?
        Examples:
        Chatbots
        Deepfakes
        4. Minimal Risk
        AI systems not falling into the above categories, which are largely unregulated.
        Examples:
        AI-enabled video games
        Spam filters
        Recommender Systems

        Assessment Process
        Review the AI startup's technology and use cases.
        Compare the AI system's purpose and functionality to the examples and definitions provided for each risk category.
        Consider the potential impact on safety, fundamental rights, and the environment.
        Classify the AI system into the appropriate risk category.
        Provide a brief explanation for the classification, referencing specific aspects of the AI Act and examples given.


        Format you answer in this way:
        AI Use Case: 
        Risk Classification: 
        Reason: 
        Do not give any intros or outros. The following are the AI Use cases of the startup you have to classify using all of the above rules:
        {all_use_cases}
        """
        print(eu_ai_act)
        return eu_ai_act
