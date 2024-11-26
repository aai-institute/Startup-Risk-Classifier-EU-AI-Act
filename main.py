from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin
from openai import OpenAI
import tiktoken
import time
import re
import openpyxl

import os
from dotenv import load_dotenv
load_dotenv()


class Selenium():
    def __init__(self):
        # chrome_profile_path = r"C:\Users\ShahrukhAzharAhsan\AppData\Local\Google\Chrome\User Data"

        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless=old")
        # chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
        chrome_options.add_argument("profile-directory=Default")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36")
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--log-level=1")

        self.__driver = webdriver.Chrome(options=chrome_options)
        # self.__driver = None
        return self.__driver

class ChatGPT():
    def __init__(self, model_name, prompt, context, client):
        self.model_name = model_name
        self.prompt = prompt
        self.context = context
        self.client = client
        print(f"ChatGPT class initialized with model {model_name}")
    
    def chat_model(self):
        self.context.append({"role": "user", "content": self.prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.context
            )

            answer = response.choices[0].message.content.strip()
            self.context.append({"role": "assistant", "content": answer})

            return [answer, self.context]
        
        except Exception as e:
            print(f"API Error: {e}")
            return [None, None]

class LinkWorker(Selenium):
    MAX_TIME_SECONDS = 10

    def __init__(self, url):
        self.__driver = super().__init__()
        self.__body_html = ""

        # Fix URL if it doesn't have the protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Rebuild the URL (keep path as-is, drop query and fragment)
        self.__parsed_url = urlparse(url)
        self.__url = urlunparse((self.__parsed_url.scheme, self.__parsed_url.netloc, self.__parsed_url.path, '', '', ''))

        return self.__driver, self.__url, self.__parsed_url

    def get_url(self):
        return self.__url
        
    def find_elements_by_xpath(self, xpath):
        try:
            elements = self.__driver.find_elements(By.XPATH, xpath)
            return elements
        except NoSuchElementException:
            print(f"Element with XPath {xpath} not found. Function: find_elements_by_xpath")
            return []
        except Exception as e:  
            print(f"Unexpected error on XPath {xpath}. Reason: {e}. Function: find_elements_by_xpath")
            return []

    def page_scroller(self):
        start_time = time.time()

        while True:
            # Scroll by viewport height
            self.__driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(0.5)

            # Calculate how far we have scrolled and how much is remaining
            scrolled_height = self.__driver.execute_script("return Math.round(window.pageYOffset);")
            total_scrollable_height = self.__driver.execute_script("return Math.round(document.body.scrollHeight);")
            visible_height = self.__driver.execute_script("return Math.round(window.innerHeight);")

            elapsed_time = time.time() - start_time

            # Break conditions: 1) We have reached the end of the page 2) Elapsed time is greater than the maximum allowed time
            if (scrolled_height + visible_height >= total_scrollable_height - 5) or (elapsed_time > LinkWorker.MAX_TIME_SECONDS):
                break
    
    def cookie_acceptor(self):
        # cookie_button_labels = ["Accept", "Agree", "Got it", "Continue", "OK", "I Accept", "I Agree", "Allow", "Accept Cookies", "Yes, I Agree", "Akzeptieren", "Einverstanden", "Zustimmen", "Fortfahren", "Alle auswählen", "Alle akzeptieren", "Alles akzeptieren", "Zustimmen und weiter"]

        cookie_button_labels = ["Accept", "Agree", "Got it", "Continue", "OK", "I Accept", "I Agree", "Allow", "Accept Cookies", "Yes, I Agree", "Akzeptieren", "Einverstanden", "Zustimmen", "Fortfahren", "Ablehnen", "Alle auswählen", "auswählen", "Alle akzeptieren", "Alles akzeptieren", "Alle ablehnen", "Zustimmen und weiter", "Alle zulassen"]

        potential_cookie_elems = self.find_elements_by_xpath("//button") + self.find_elements_by_xpath("//a")
        for element in potential_cookie_elems:
            potential_cookie_word = element.text.strip()
            # Compare only in lowercase
            if potential_cookie_word.lower() in [x.lower() for x in cookie_button_labels]:
                element.click()
                print(f"Cookie acceptor found and clicked: {potential_cookie_word}")
                time.sleep(1)
                return True
        
        print("Cookie acceptor not found")
        return False
        
    def get_base_domain(self):
        # Extract the netloc (Remove the port number, if any)
        netloc = self.__parsed_url.netloc.split(":")[0] 
        
        # Remove 'www.' if present
        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc

    def quit_driver(self):
        self.__driver.quit()

    def count_tokens(self, text, model_name):
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    
    def clean_text(self, text):
        # Clean the text: Remove extra spaces and newlines
        return re.sub(r'\s+', ' ', text).strip()

    # Retreive the innerHTML of the body tag, do not clean it
    def set_body_innerHTML(self):
        body_element = self.__driver.find_element(By.TAG_NAME, "body")
        self.__body_html = body_element.get_attribute("innerHTML")

    # Parse the HTML content into text
    def get_body_text(self):
        soup = BeautifulSoup(self.__body_html, "html.parser")
        all_text = soup.get_text(separator=" ")
        return self.clean_text(all_text)

    def get_page_content(self, model_name):
        # print(self.__body_html)

        all_text = self.get_body_text()

        body_length = len(all_text)
        print(f"Page character length: {body_length}")
        tokens = self.count_tokens(all_text, model_name)

        while tokens > 8000:
            print(f"Token count: {tokens}. Text too long. Truncating 100 letters.")
            all_text = all_text[:-100]
            tokens = self.count_tokens(all_text, model_name)
        
        print(f"Token count in raw page: {tokens}")

        return all_text
    
    def get_page_links(self):
        soup = BeautifulSoup(self.__body_html, "html.parser")
        links = soup.find_all("a", href=True)

        same_domain_links = []
        for link in links:
            full_link = urljoin(self.__url, link['href'])  # Resolve relative URL
            parsed_link = urlparse(full_link)

            if self.get_base_domain() == parsed_link.netloc and full_link not in same_domain_links:
                same_domain_links.append(full_link)
            
            if len(same_domain_links) > 80:
                break

        return same_domain_links



class WebScraper(LinkWorker):
    def __init__(self, url):
        self.__driver, self.__url, self.__parsed_url = super().__init__(url)
        
    def open_url(self):
        try:
            self.__driver.get(self.__url)
            print(f"URL {self.__url} opened successfully")
        except Exception as e:
            print(f"Error opening URL {self.__url}. Reason: {e}. Function: goto_url")


class Prompts():
    def __init__(self, startupName, raw_text):
        self.startupName = startupName
        self.raw_text = raw_text
        
    def startup_summary(self):
        startup_summary = f"The following is the content of the homepage of a company's website whose supposed name is \"{self.startupName}\", but confirm this from the homepage content. \n\nYour task is to generate all the AI use cases this company is implementing. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing. If the content of this webpage is just a page error, then output 'Page Error' only. \n\nContent of the homepage: {self.raw_text}"

        return startup_summary


def main():
    sheet = openpyxl.load_workbook("raw-dealroom.xlsx")["Sheet1"]

    for row in range(2, sheet.max_row + 1):
        url = sheet.cell(row=row, column=4).value
        startup_name = sheet.cell(row=row, column=2).value
        
        print(f"Startup Name: {startup_name}")
        print(f"URL: {url}\n")

    # url = "https://findiq.de/"
    # model_name = "gpt-4o"

    # web_scraper = WebScraper(url)

    # web_scraper.open_url()
    # web_scraper.cookie_acceptor()
    # web_scraper.page_scroller()
    
    # web_scraper.set_body_innerHTML()
    # page_content = web_scraper.get_page_content(model_name)
    # page_links = web_scraper.get_page_links()

    # # print(f"Page content: {page_content}")
    # # print(f"Page links: {page_links}")

    # prompts = Prompts("FindIQ", page_content)

    # summary_model = ChatGPT(model_name, startup_summary_prompt("FindIQ", page_content), [], OpenAI(api_key=os.getenv("MY_KEY")))
    # summary, summary_context = summary_model.chat_model()

    # print(f"Summary: {summary}")

    # time.sleep(100)





def startup_summary_prompt(startupName, raw_text):
    startup_summary = f"The following is the content of the homepage of a company's website whose supposed name is \"{startupName}\", but confirm this from the homepage content. \n\nYour task is to generate all the AI use cases this company is implementing. You can also use your own knowledge to help with this task. Do not guess any use case, only find the ones that the company is actually implementing. If the content of this webpage is just a page error, then output 'Page Error' only. \n\nContent of the homepage: {raw_text}"

    return startup_summary






if __name__ == "__main__":
    main()