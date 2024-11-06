import json
import logging
from pathlib import Path
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Optional

class ItchAutomation:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the automation with config file path."""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self._setup_logging()
        self.driver = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                required_fields = ['game_id', 'itchio_cookie']
                if not all(field in config for field in required_fields):
                    raise ValueError(f"Config must contain {required_fields}")
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in config file")

    def _setup_logging(self):
        """Configure logging for the automation."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('itch_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_browser(self) -> None:
        """Initialize and configure the Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Add the authentication cookie
        cookie = {
            'name': 'itchio',
            'value': self.config['itchio_cookie'],
            'domain': '.itch.io'
        }
        self.logger.info("Setting up browser with authentication")
        self.driver.get('https://itch.io')
        self.driver.add_cookie(cookie)

    def get_edit_page(self) -> Optional[str]:
        """
        Navigate to the game edit page using Selenium.
        Returns the page source if successful.
        """
        if not self.driver:
            self.setup_browser()

        url = f"https://itch.io/game/edit/{self.config['game_id']}"
        try:
            self.logger.info(f"Accessing edit page for game ID {self.config['game_id']}")
            self.driver.get(url)
            
            # Wait for a common element that would be present on the edit page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error accessing edit page: {str(e)}")
            return None
        
    def get_edit_page_requests(self) -> Optional[str]:
        """
        Alternative method using requests library instead of Selenium.
        Useful for simpler operations that don't require JavaScript.
        """
        url = f"https://itch.io/game/edit/{self.config['game_id']}"
        cookies = {'itchio': self.config['itchio_cookie']}
        
        try:
            self.logger.info(f"Requesting edit page for game ID {self.config['game_id']}")
            response = self.session.get(url, cookies=cookies)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request: {str(e)}")
            return None

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser session closed")

def main():
    """Main execution function."""
    automation = ItchAutomation()
    
    try:
        # Try with Selenium first (for JavaScript-heavy pages)
        content = automation.get_edit_page()
        
        # Fall back to requests if Selenium fails or isn't needed
        if not content:
            content = automation.get_edit_page_requests()
        
        if content:
            # Save the page content for debugging/verification
            with open('latest_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully retrieved and saved page content")
        else:
            print("Failed to retrieve page content")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main()
