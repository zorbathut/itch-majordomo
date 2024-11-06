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

    def update_display_names(self, name_mappings: dict):
        """
        Update display names based on filename mappings.
        Args:
            name_mappings: Dict mapping upload_fname to desired display_name
        """
        uploaders = self.driver.find_elements(By.CLASS_NAME, "uploader")
        self.logger.info(f"Found {len(uploaders)} upload entries")
        
        for uploader in uploaders:
            # Find the filename element
            fname_elem = uploader.find_element(By.CLASS_NAME, "upload_fname")
            filename = fname_elem.text
            
            if filename in name_mappings:
                # Find the hidden input for display_name
                display_input = uploader.find_element(By.CSS_SELECTOR, 'input[name$="[display_name]"]')
                
                # Update the display name
                new_name = name_mappings[filename]
                self.driver.execute_script(
                    'arguments[0].value = arguments[1]',
                    display_input,
                    new_name
                )
                self.logger.info(f"Updated {filename} display name to {new_name}")

    def save_changes(self, timeout: int = 30):
        """
        Click the save button and wait for save confirmation.
        Args:
            timeout: How long to wait for save confirmation in seconds
        Returns:
            bool: True if save was confirmed, False if timeout
        """
        save_btn = self.driver.find_element(By.CLASS_NAME, "save_btn")
        save_btn.click()
        self.logger.info("Clicked save button")
        
        # Wait for either success or error message
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: 
            any(msg.is_displayed() for msg in driver.find_elements(By.CLASS_NAME, "global_flash"))
        )
        
        # Check if it was successful
        messages = self.driver.find_elements(By.CLASS_NAME, "global_flash")
        for msg in messages:
            if msg.is_displayed():
                self.logger.info(f"Save result: {msg.text}")
                return "saved" in msg.text.lower()

    def cleanup(self):
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser session closed")

def main():
    automation = ItchAutomation(headless=False)
    try:
        automation.navigate_to_edit_page()

        print(automation.driver.page_source)

        # Example usage:
        name_mappings = {
            "project-tsoh-linux.zip": "project-tsoh-linux-test2.zip",
            "project-tsoh-windows.zip": "project-tsoh-windows-test2.zip"
        }
        
        automation.update_display_names(name_mappings)
        automation.save_changes()
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main()