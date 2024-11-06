import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class ItchAutomation:
    def __init__(self, config_path: str = "config.json", headless: bool = False):
        self.config = self._load_config(config_path)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self._authenticate()
        
    def _load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            config = json.load(f)
            if not all(field in config for field in ['game_id', 'itchio_cookie']):
                raise ValueError("Config must contain 'game_id' and 'itchio_cookie'")
            return config

    def _authenticate(self):
        self.driver.get('https://itch.io')
        cookie = {
            'name': 'itchio',
            'value': self.config['itchio_cookie'],
            'domain': '.itch.io'
        }
        self.driver.add_cookie(cookie)
        self.logger.info("Authentication cookie set")

    def navigate_to_edit_page(self):
        url = f"https://itch.io/game/edit/{self.config['game_id']}"
        self.logger.info(f"Navigating to edit page for game ID {self.config['game_id']}")
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def cleanup(self):
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser session closed")

def main():
    automation = ItchAutomation(headless=False)
    try:
        automation.navigate_to_edit_page()

        print(automation.driver.page_source)
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main()