from Classes.LinkWorker import LinkWorker
from selenium.common.exceptions import TimeoutException
import re

class WebScraper(LinkWorker):
    def __init__(self):
        self.__driver = super().__init__()
        self.__total_token_cost = 0
        self.__redirected_url = ""

    def set_token_cost(self, input_tokens, output_tokens, model_name):
        if model_name == "chatgpt-4o-latest":
            input_cost = (input_tokens / 1000) * 0.005
            output_cost = (output_tokens / 1000) * 0.015
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "gpt-4o-mini":
            input_cost = (input_tokens / 1000) * 0.00015
            output_cost = (output_tokens / 1000) * 0.0006
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "o3-mini":
            input_cost = (input_tokens / 1000) * 0.0011
            output_cost = (output_tokens / 1000) * 0.0044
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "gpt-4o":
            input_cost = (input_tokens / 1000) * 0.0025
            output_cost = (output_tokens / 1000) * 0.01
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "claude-3-7-sonnet-20250219":
            input_cost = (input_tokens / 1000) * 0.003
            output_cost = (output_tokens / 1000) * 0.015
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "gpt-4o-search-preview":
            input_cost = (input_tokens / 1000) * 0.0025
            output_cost = (output_tokens / 1000) * 0.01
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "deepseek-reasoner":
            input_cost = (input_tokens / 1000) * 0.00055
            output_cost = (output_tokens / 1000) * 0.00219
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "gemini-1.5-pro":
            # for input and output tokens <= 128k tokens
            input_cost = (input_tokens / 1000) * 0.00125
            output_cost = (output_tokens / 1000) * 0.005
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "gemini-2.0-flash-thinking-exp-01-21":
            # This cost is taken from the Gemini 2.0 Flash model
            input_cost = (input_tokens / 1000) * 0.0001
            output_cost = (output_tokens / 1000) * 0.0004
            self.__total_token_cost += input_cost + output_cost
        else:
            raise ValueError("Model name not recognized. Token cost not calculated.")

    # --- Token methods ---
    def get_token_cost(self):
        return self.__total_token_cost

    def reset_token_cost(self):
        self.__total_token_cost = 0

    # --- URL methods ---
    def get_url(self):
        return self.__url
    
    def set_url(self, url):
        self.__url = self.clean_url(url)
        # print(f"Original URL: {url}. Cleaned URL: {self.__url}")

    # --- Redirection methods ---
    def set_redirect_url(self, redirected_url):
        self.__redirected_url = redirected_url

    def get_redirected_url(self):
        return self.__redirected_url
    
    def reset_redirect_url(self):
        self.__redirected_url = ""

    def open_url(self):
        try:
            self.__driver.set_page_load_timeout(15)  # Set the timeout to 15 seconds
            self.__driver.get(self.__url)

            if self.__driver.current_url != self.__url:
                print(f"Redirected to {self.__driver.current_url}")
                self.set_redirect_url(self.__driver.current_url)
                self.set_url(self.__driver.current_url)
            return 200
        except TimeoutException:
            print(f"Page load timeout: {self.__url}. Stopping page load.")
            self.__driver.execute_script("window.stop();")  # Stop the loading
        except Exception as e:
            print(f"Error opening URL {self.__url}")
            return 0 # General Error

    def quit_driver(self):
        self.__driver.quit()

    def load_page(self):
        status = self.open_url()
        # If there was a DNS failure, toggle the www. part and try again
        if status == 0:  
            current_url = self.get_url()
            new_url = self.toggle_www(current_url)

            if new_url:
                print(f"Retrying with {new_url}")
                self.set_url(new_url)
                status = self.open_url()

                if status == 0:
                    print("Toggling www did not work.")
                    self.set_url(current_url)  # Reset to original URL
                else:
                    self.set_redirect_url(self.get_url())


        self.cookie_acceptor()
        self.page_scroller()
        self.set_html_innerHTML()

    def get_page_content(self, model_name):
        page_content = self.scrape_page_content(model_name)
        return page_content
    
    def get_page_links(self):
        page_links = self.scrape_page_links(self.__url)
        return page_links


