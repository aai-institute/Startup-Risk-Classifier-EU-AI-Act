from Classes.Selenium import Selenium
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin
import time
import re
import tiktoken
from openpyxl.utils.escape import escape


class LinkWorker(Selenium):
    MAX_TIME_SECONDS = 10

    def __init__(self):
        self.__driver = super().__init__()
        self.__body_html = ""
        
        # Rebuild the URL (keep path as-is, drop query and fragment)
        # self.__url = self.clean_url(url)

        return self.__driver

    def clean_url(self, url):
        # set the right protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        elif url.startswith("http://"):
            url = url.replace("http://", "https://")

        parsed_url = urlparse(url)
        # Normalize empty path to '/'
        path = parsed_url.path if parsed_url.path else '/'
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.hostname, path, '', '', ''))
        return cleaned_url


    def toggle_www(self, url):
        if "www." in url:
            return url.replace("www.", "", 1)  # Remove 'www.' only once
        else:
            parts = url.split("://")
            if len(parts) == 2:
                return f"{parts[0]}://www.{parts[1]}"  # Add 'www.'
        return None  # Return None if modification is not possible

    def find_elements_by_xpath(self, xpath):
        try:
            elements = self.__driver.find_elements(By.XPATH, xpath)
            return elements
        except NoSuchElementException:
            # print(f"Element with XPath {xpath} not found. Function: find_elements_by_xpath")
            return []
        except Exception as e:  
            # print(f"Unexpected error on XPath {xpath}. Reason: {e}. Function: find_elements_by_xpath")
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
        cookie_button_labels = ["Accept", "Accept All", "Allow All", "Agree", "Got it", "Continue", "OK", "I Accept", "I Agree", "Allow", "Accept Cookies", "Yes, I Agree", "Akzeptieren", "Einverstanden", "Zustimmen", "Fortfahren", "Ablehnen", "Alle auswählen", "auswählen", "Alle akzeptieren", "Alles akzeptieren", "Alle ablehnen", "Zustimmen und weiter", "Alle zulassen"]

        potential_cookie_elems = self.find_elements_by_xpath("//button") + self.find_elements_by_xpath("//a")
        for element in potential_cookie_elems:
            try:
                potential_cookie_word = element.text.strip()
                # Compare only in lowercase
                if potential_cookie_word.lower() in [x.lower() for x in cookie_button_labels]:
                    element.click()
                    # print(f"Cookie acceptor found and clicked: {potential_cookie_word}")
                    time.sleep(1)
                    return True
            except StaleElementReferenceException:
                # print("StaleElementReferenceException encountered. Retrying...")
                continue  # Retry by checking the next element
            except NoSuchElementException:
                # print("NoSuchElementException: Element may have been removed.")
                continue
            except Exception as e:
                # print(f"An unexpected exception occurred: {e}")
                continue
        
        # print("Cookie acceptor not found")
        return False

    def count_tokens(self, text, model_name):
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    
    def clean_text(self, text):
        # Clean the text: Remove extra spaces and newlines
        return re.sub(r'\s+', ' ', text).strip()

    # Retreive the innerHTML of the html tag, do not clean it
    def set_html_innerHTML(self):
        body_element = self.__driver.find_element(By.TAG_NAME, "html")
        self.__body_html = body_element.get_attribute("innerHTML")

    # Parse the HTML content into text
    def get_body_text(self):
        soup = BeautifulSoup(self.__body_html, "html.parser")
        all_text = soup.get_text(separator=" ")
        
        # Combine <iframe> and <frame> handling
        iframe_text = ""
        frames = self.__driver.find_elements(By.TAG_NAME, "iframe") + self.__driver.find_elements(By.TAG_NAME, "frame")
        for frame in frames:
            try:
                self.__driver.switch_to.frame(frame)  # Switch to the frame/iframe
                frame_soup = BeautifulSoup(self.__driver.page_source, "html.parser")
                iframe_text += frame_soup.get_text(separator=" ")
                self.__driver.switch_to.default_content()  # Switch back to the main content
            except WebDriverException:
                # Skip if the frame/iframe is restricted or inaccessible
                continue
        
        # Combine the main content and iframe/frame content
        all_text += "\n\n" + iframe_text
        return self.clean_text(all_text)

    def scrape_page_content(self, model_name):
        # print(self.__body_html)

        all_text = self.get_body_text()

        body_length = len(all_text)
        # print(f"Page character length: {body_length}")
        tokens = self.count_tokens(all_text, model_name)
            
        while tokens > 8000:
            print(f"Token count: {tokens}. Text too long. Truncating 1000 letters.")
            all_text = all_text[:-1000]
            tokens = self.count_tokens(all_text, model_name)
        
        # print(f"Token count in raw page: {tokens}")

        # Remove illegal characters that would not save in Excel
        all_text = escape(all_text)

        return all_text
    
    def scrape_page_links(self, source_url):
        soup = BeautifulSoup(self.__body_html, "html.parser")
        links = soup.find_all("a", href=True)

        same_domain_links = []
        for link in links:
            url_found = self.clean_url(urljoin(source_url, link['href']))  # Resolve relative URL and clean
            parsed_link = urlparse(url_found)
            # print(f"Found URL: {url_found}")

            # Check if the found url is from the main domain, not already in the list and not the source URL (i.e. homepage)
            if urlparse(source_url).hostname == parsed_link.hostname and url_found not in same_domain_links and url_found != source_url:
                same_domain_links.append(url_found)
            
            if len(same_domain_links) > 80:
                break

        # print(f"Links found: {same_domain_links}")
        return same_domain_links
