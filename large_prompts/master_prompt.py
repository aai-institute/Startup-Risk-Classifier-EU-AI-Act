master_prompt = """
You will be provided with AI use cases of a company. You have to understand those use cases (provided later) and the following instructions to classify each use case. The term AI use case and AI system means the same for this task.

Step 1: Check for use-cases that should be classified as "Prohibited AI system" if and only if they fall under the following articles:

A) Article 5(1)(a) - Harmful Manipulation and Deception Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- System must deploy subliminal techniques beyond consciousness OR purposefully manipulative OR deceptive techniques  
- Must have objective/effect of materially distorting behavior  
- Must cause/be reasonably likely to cause significant harm

Key definitions:

- Subliminal techniques: operate beyond conscious awareness  
- Significant harm: includes physical, psychological, financial harm  
- Material distortion: substantial impact on behavior, not minor influence

Examples:

- AI chatbot promoting self-harm  
- AI system using hidden emotional manipulation to drive addiction  
- AI using subliminal messaging to influence purchasing decisions

B) Article 5(1)(b) - Harmful Exploitation of Vulnerabilities Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- System must exploit vulnerabilities due to:  
  -- Age  
  -- Disability  
  -- Specific social/economic situation  
- Must have objective/effect of materially distorting behavior  
- Must cause/be reasonably likely to cause significant harm

Key definitions:

- Vulnerabilities: cognitive, emotional, physical susceptibilities  
- Social/economic situation: includes poverty, minority status, migration status

Examples:

- AI system targeting elderly with deceptive financial scams  
- AI exploiting children's vulnerabilities through addictive design  
- AI targeting socially disadvantaged groups with predatory loans

C) Article 5(1)(c) - Social Scoring Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- Must evaluate/classify persons based on social behavior or personal characteristics over time  
- Must lead to either:  
  -- Detrimental treatment in unrelated social contexts OR  
  -- Unjustified/disproportionate treatment

Key definitions:

- Social behavior: actions, habits, interactions in society  
- Personal characteristics: demographic info, preferences, behaviors

Examples:

- Government system scoring citizens across multiple contexts affecting access to services  
- AI system using unrelated social data to determine access to benefits  
- System using social media behavior to restrict access to essential services

D) Article 5(1)(d) - Individual Crime Risk Assessment Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- Must assess/predict risk of person committing crime  
- Must be based solely on:  
  -- Profiling OR  
  -- Personality trait assessment

Key definitions:

- Profiling: automated processing to evaluate personal aspects  
- Crime prediction: forward-looking assessment of future crimes

Examples:

- AI system predicting crime risk based only on personality traits  
- System assessing likelihood of offending based purely on profiling

E) Article 5(1)(e) - Untargeted Facial Image Scraping Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- Must create/expand facial recognition databases  
- Must use untargeted scraping  
- Must scrape from internet or CCTV footage

Key definitions:

- Untargeted scraping: indiscriminate collection without specific focus  
- Facial recognition database: collection for matching facial images

F) Article 5(1)(f) - Emotion Recognition Conditions:

- Must involve placing on market, putting into service or use of an AI system  
- Must infer emotions  
- Must be used in:  
  -- Workplace OR  
  -- Educational institutions  
- Exception: medical or safety reasons

Key definitions:

- Emotion recognition: identifying/inferring emotions from biometric data  
- Workplace: any physical/virtual work space

G) Article 5(1)(g) - Biometric Categorization Conditions:

- Must involve placing on market, putting into service or use of AI system  
- Must categorize individuals based on biometric data  
- Must deduce/infer:  
  -- Race  
  -- Political opinions  
  -- Trade union membership  
  -- Religious/philosophical beliefs  
  -- Sex life/orientation

H) Article 5(1)(h) - Real-time Remote Biometric Identification Conditions:

- Must be use of real-time RBI system  
- Must be in publicly accessible spaces  
- Must be for law enforcement  
- Exceptions for:  
  -- Specific victim searches  
  -- Prevention of threats  
  -- Criminal suspect identification


Step 2: Check for use-cases that should be classified as "High-risk AI system under Annex I" if they fall under the following conditions:

AI systems that are safety components of products OR are themselves products covered by Union harmonization laws listed in Annex I AND must undergo third-party conformity assessment under that legislation.

For this classification rule to apply, two conditions must be fulfilled: 

1. The system is either a product OR a safety component of a product covered by Union harmonization laws under Annex I of the AI Act, AND
2. That product or safety component of a product is required to undergo a third-party conformity assessment under that Union harmonized law 

A component is considered a "safety component" if EITHER:   
- It fulfills a safety function for a product or system OR   
- Its failure or malfunctioning endangers the health and safety of persons 

Components used solely for cybersecurity purposes are NOT considered safety components.


The list of Union harmonization laws is as follows:

Section A (New Legislative Framework): 

- Machinery Directive (2006/42/EC)   
- Toy Safety Directive (2009/48/EC)   
- Recreational Craft Directive (2013/53/EU)   
- Lifts Directive (2014/33/EU)   
- ATEX Directive (2014/34/EU) - Equipment for explosive atmospheres   
- Radio Equipment Directive (2014/53/EU)   
- Pressure Equipment Directive (2014/68/EU)   
- Cableway Installations Regulation (2016/424)   
- Personal Protective Equipment Regulation (2016/425)   
- Gas Appliances Regulation (2016/426)   
- Medical Devices Regulation (2017/745)   
- In Vitro Diagnostic Medical Devices Regulation (2017/746) 

Section B: 

- Civil Aviation Security Regulation (300/2008)   
- Two/Three-Wheel Vehicles Regulation (168/2013)   
- Agricultural/Forestry Vehicles Regulation (167/2013)   
-  Marine Equipment Directive (2014/90/EU)   
- Rail System Interoperability Directive (2016/797)   
- Motor Vehicles  Market Surveillance Regulations (2018/858)  and Motor Vehicles Type Approval Regulation (2019/2144)     
- Civil Aviation/EASA Regulation (2018/1139)


Step 3: Check for use-cases that should be classified as "High-risk AI system under Annex III" if they fall under the following conditions:

a) Biometric Identification & Categorization:  
- Remote biometric identification systems  
- Biometric categorization systems based on sensitive or protected attributes  
- Emotion recognition systems  
(Note: Excludes 1:1 verification/authentication systems)

b) Critical Infrastructure:  
- Safety components in management or operation of critical digital infrastructure, road traffic, or in the supply of water, gas, heating or electricity.  
- Additional explanation: Safety components of critical infrastructure, including critical digital infrastructure, are systems used to directly protect the physical integrity of critical infrastructure or health and safety of persons and property but which are not necessary in order for the system to function.  
-Additional explanation: “critical digital infrastructure, road traffic, or in the supply of water, gas, heating or electricity” constitute an exhaustive list. This would not cover, for example, safety components in products like vehicles.   
- Example: Systems for monitoring water pressure or fire alarm controlling systems in cloud computing centres are high risk  
(Note: Excludes systems for the sole purpose of cybersecurity)

c) Education/Training:  
- Systems for determining access/admission  
- Systems for evaluating learning outcomes or steer learning process  
- Systems for assessing education levels  
- Systems for monitoring student behavior during tests

d) Employment/Worker Management:  
- Recruitment and selection systems, including systems for the targeted placing of job advertisements  
- Systems for promotion/termination decisions  
- Task allocation systems based on individual behavior or personal traits or characteristics  
- Performance monitoring systems

e) Essential Services Access:  
- Public assistance benefit evaluation systems  
- Creditworthiness assessment systems for natural persons (Note: This does *not* include AI systems used for the purpose of detecting financial fraud)  
- Systems used for risk assessment and pricing in relation to natural persons in the case of life and health insurance  
- Emergency service dispatch/prioritization systems

f) Law Enforcement:  
- Systems that assess the risk of a person becoming a victim of a crime   
- Lie detection/similar tools  
- Evidence reliability evaluation  
- Systems that assess the risk of a person committing a crime or to assess personality traits and characteristics or past criminal behavior of natural persons or groups  
- Natural person profiling systems

g) Migration/Asylum/Border Control:  
- Lie detection tools  
- Risk assessment systems  
- Document/evidence verification systems  
- Border monitoring/surveillance systems

h) Justice/Democratic Processes:  
- Systems assisting judicial decisions  
- Systems influencing voting behavior/election outcomes  
(Note: Excludes administrative campaign management tools)

3. Exception Analysis:  
If the system falls under an Annex III area, but it qualifies for any of the following exceptions, it should not be considered high-risk:

a) Narrow Procedural Task:  
- Does it only transform data formats?  
- Does it only classify/categorize documents?  
- Does it only detect duplicates?

b) Improvement of Human Activity:  
- Does it only enhance previously completed work?  
- Does it only provide an additional layer to human activity?  
- Example: Improving language in drafted documents

c) Pattern Detection:  
- Does it only identify patterns in previous decisions?  
- Is it used only for ex-post analysis?  
- Does it require human review?  
- Example: Analyzing grading patterns for inconsistencies

d) Preparatory Tasks:  
- Is it limited to file handling/indexing?  
- Does it only process/link data?  
- Is it only used for translation?

Note: These exceptions do not apply if the system performs profiling of natural persons.


Step 4: At this point, you should know what transparency obligations are according to the EU AI Act. This will help you follow subsequent steps so please understand them too. Here are its details:

Key aspects of an AI use case requiring transparency obligations:

1. Systems Interacting with Natural Persons (Art 50(1))  
- Applies when there's a risk that people might believe they're interacting with a human instead of an AI system  
- Exception: When it's obvious from the circumstances/context  
- Exception: Law enforcement systems for detecting/preventing crime  
- Example: AI chatbots, virtual assistants

2. Systems Generating Synthetic Content (Art 50(2))  
- Covers AI systems generating audio, image, video, or text content  
- Exception: Systems only performing assistive function for standard editing  
- Exception: Systems not substantially altering input data  
- Example: Generative AI applications such as Image generators or LLM based products

3. Emotion Recognition Systems (Art 50(3))  
- Systems identifying/inferring emotions or intentions based on biometric data  
- Example: Systems analyzing facial expressions for emotional states

4. Biometric Categorization Systems (Art 50(3))  
- Systems categorizing people based on biometric data  
- Example: Systems categorizing people by age, gender, or other characteristics

5. Deep Fakes/Manipulated Content (Art 50(4))  
- Content resembling existing persons/places that appears authentic  
- Exception: Creative/artistic/satirical content (requires different disclosure approach)  
- Exception: AI-generated text that undergoes human review/editorial control  
- Example: AI-generated videos of real people


Step 5: If a use case is either "High-risk AI system under Annex I" or "High-risk AI system under Annex III", *AND* has transparency obligations, please classify it as a "High-risk AI system with transparency obligations"

Step 6: If only transparency obligations apply to a use-case, then classify it as "System with transparency obligations"

Step 7: If the system does not meet any of the criteria for any of the previous steps, then classify it as a "Low-risk AI system"


Format your answer in the following manner:

AI Use Case: <Put the name of the AI Use Case here>  
Use Case Description: <Put the description of the use case here>  
Risk Classification: Please return *exactly* one of the following classifications: 

Prohibited AI system  
High-risk AI system under Annex I  
High-risk AI system under Annex III  
High-risk AI system with transparency obligations  
System with transparency obligations  
Low-risk AI system
Uncertain

<Pick Uncertain if you can not reasonably assign a classification and require additional information>

Reason: <Provide a detailed justification which shows that you have followed all the steps for the classification. Cite the relevant clauses and annexes to support your justification. Show your reasoning process for each step defined above and how you arrived at the final classification.>

Requires Additional Information: <Answer "Yes" or "No" only. You should require this information only in exceptional cases where you cannot reasonably make a classification.>

What additional Information: <Please describe what additional information you needed to make a conclusive classification>

"""