from selenium import webdriver
import tempfile

class Selenium():
    def __init__(self):
        unique_dir = tempfile.mkdtemp()
        # chrome_profile_path = r"C:\Users\ShahrukhAzharAhsan\AppData\Local\Google\Chrome\User Data"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"user-data-dir={unique_dir}")
        # chrome_options.add_argument("profile-directory=Default")
        
        # Reuqired for running in docker
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues. Also required in docker because shared memory is 64mb only in docker.


        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        chrome_options.add_argument('--window-size=1920,1080')
        # chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--log-level=1")

        # Disable GPU
        # chrome_options.add_argument("--disable-gpu")  # Disables GPU acceleration
        # chrome_options.add_argument("--disable-software-rasterizer")  # Further prevents GPU issues
        chrome_options.add_argument("--enable-webgl")


        self.__driver = webdriver.Chrome(options=chrome_options)


        # self.__driver = None
        return self.__driver
