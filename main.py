from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse
from openai import OpenAI
import time

class Selenium():
    def __init__(self):
        # chrome_profile_path = r"C:\Users\ShahrukhAzharAhsan\AppData\Local\Google\Chrome\User Data"

        # chrome_options = webdriver.ChromeOptions()
        # # chrome_options.add_argument("--headless=old")
        # # chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
        # chrome_options.add_argument("profile-directory=Default")
        # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36")
        # chrome_options.add_argument('--window-size=1920,1080')
        # chrome_options.add_argument("--incognito")
        # chrome_options.add_argument("--log-level=1")

        # self.__driver = webdriver.Chrome(options=chrome_options)
        self.__driver = None
        return self.__driver

class ChatGPT():
    def __init__(self, model_name, prompt, context, client):
        self.model_name = model_name
        self.prompt = prompt,
        self.context = context,
        self.client = client
    
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

        # Fix URL if it doesn't have the protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Rebuild the URL (keep path as-is, drop query and fragment)
        self.__parsed_url = urlparse(url)
        self.__url = urlunparse((self.__parsed_url.scheme, self.__parsed_url.netloc, self.__parsed_url.path, '', '', ''))
 
    def get_url(self):
        return self.__url
        
    def goto_url(self):
        try:
            self.__driver.get(self.__url)
            print(f"URL {self.__url} opened successfully")
        except Exception as e:
            print(f"Error opening URL {self.__url}. Reason: {e}. Function: goto_url")

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



def main():
    url = "https://findiq.de/"
    link_worker = LinkWorker(url)

    # link_worker.goto_url()
    
    # link_worker.cookie_acceptor()
    # link_worker.page_scroller()


    additional_urls = [
    'https://sub.example.com/path/file.html',
    'http://example.com',
    'https://example.co.uk/path/file',
    'ftp://example.com/resource',
    'https://www.example.com:8080/path/file',
    'https://example.com/path/file.html?q=123#section1',
    'https://example.com/path/file.html?q=123',
    'https://example.com/path/file.html#section1',
    'https://example.com/path/file',
    'https://example.com/path/file/'
]

    for link in additional_urls:
        link_worker = LinkWorker(link)
        print(f"Orignal URL: {link}")
        print(f"Fixed URL: {link_worker.get_url()}")
        print(f"Base Domain: {link_worker.get_base_domain()}\n")
    # chat_gpt = ChatGPT("gpt-3.5-turbo", "What is the capital of France?", [], OpenAI())
    # response, context = chat_gpt.chat_model()
    # print(f"Response: {response}")
    # print(f"Context: {context}")

    # link_worker.quit_driver()

if __name__ == "__main__":
    main()