from Classes.LinkWorker import LinkWorker

class WebScraper(LinkWorker):
    def __init__(self, url):
        self.__driver, self.__url = super().__init__(url)
        self.__total_input_tokens = 0
        self.__total_output_tokens = 0
        
    def increase_input_tokens(self, tokens):
        self.__total_input_tokens += tokens
    def increase_output_tokens(self, tokens):
        self.__total_output_tokens += tokens
    def get_total_input_tokens(self):
        return self.__total_input_tokens
    def get_total_output_tokens(self):
        return self.__total_output_tokens

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
        self.set_body_innerHTML()

    def get_page_content(self, model_name):
        page_content = self.scrape_page_content(model_name)
        return page_content
    
    def get_page_links(self):
        page_links = self.scrape_page_links()
        return page_links
