from Classes.LinkWorker import LinkWorker

class WebScraper(LinkWorker):
    def __init__(self, url):
        self.__driver, self.__url = super().__init__(url)
        self.__total_token_cost = 0

    def set_token_cost(self, input_tokens, output_tokens, model_name):
        if model_name == "chatgpt-4o-latest":
            input_cost = (input_tokens / 1000) * 0.005
            output_cost = (output_tokens / 1000) * 0.015
            self.__total_token_cost += input_cost + output_cost
        elif model_name == "o1-preview":
            input_cost = (input_tokens / 1000) * 0.015
            output_cost = (output_tokens / 1000) * 0.06
            self.__total_token_cost += input_cost + output_cost
        else:
            raise ValueError("Model name not recognized. Token cost not calculated.")
    
    def get_token_cost(self):
        return self.__total_token_cost

    def quit_driver(self):
        self.__driver.quit()

    def get_url(self):
        return self.__url
    
    def set_url(self, url):
        self.__url = self.clean_url(url)

    def open_url(self):
        try:
            self.__driver.get(self.__url)
            # print(f"URL {self.__url} opened successfully")
        except Exception as e:
            print(f"Error opening URL {self.__url}. Reason: {e}. Function: goto_url")

    def load_page(self):
        self.open_url()
        self.cookie_acceptor()
        self.page_scroller()
        self.set_html_innerHTML()

    def get_page_content(self, model_name):
        page_content = self.scrape_page_content(model_name)
        return page_content
    
    def get_page_links(self):
        page_links = self.scrape_page_links()
        return page_links
