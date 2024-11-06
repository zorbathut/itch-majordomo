import logging
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class ItchMajordomo:
    """
    A class for automating itch.io game page management.
    
    Args:
        game_id: The ID of the game to manage
        cookie: The itch.io authentication cookie value
        headless: Whether to run the browser in headless mode (default: True)
    
    Example:
        >>> majordomo = ItchMajordomo("123456", "your_cookie_value")
        >>> majordomo.update_display_names({
        ...     "game-linux.zip": "Linux Build v1.0",
        ...     "game-windows.zip": "Windows Build v1.0"
        ... })
        >>> majordomo.cleanup()
    """
    
    def __init__(self, game_id: str, cookie: str, headless: bool = True):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        
        # Set up authentication and navigate to page
        self.driver.get('https://itch.io')
        self.driver.add_cookie({
            'name': 'itchio',
            'value': cookie,
            'domain': '.itch.io'
        })
        
        # Navigate to edit page
        self.driver.get(f"https://itch.io/game/edit/{game_id}")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def update_display_names(self, name_mappings: Dict[str, str]) -> bool:
        """
        Update display names of uploaded files and save changes.
        
        Args:
            name_mappings: Dict mapping filename to new display name
        
        Returns:
            bool: True if save was successful
        """
        # Update the names
        uploaders = self.driver.find_elements(By.CLASS_NAME, "uploader")
        self.logger.info(f"Found {len(uploaders)} upload entries")
        
        updated = False
        for uploader in uploaders:
            fname_elem = uploader.find_element(By.CLASS_NAME, "upload_fname")
            filename = fname_elem.text
            
            if filename in name_mappings:
                display_input = uploader.find_element(
                    By.CSS_SELECTOR, 
                    'input[name$="[display_name]"]'
                )
                new_name = name_mappings[filename]
                self.driver.execute_script(
                    'arguments[0].value = arguments[1]',
                    display_input,
                    new_name
                )
                self.logger.info(f"Updated {filename} display name to {new_name}")
                updated = True
        
        if not updated:
            self.logger.warning("No matching files found to update")
            return False
            
        # Save the changes
        save_btn = self.driver.find_element(By.CLASS_NAME, "save_btn")
        save_btn.click()
        self.logger.info("Clicked save button")
        
        # Wait for save confirmation
        self.wait.until(lambda driver: 
            any(msg.is_displayed() for msg in 
                driver.find_elements(By.CLASS_NAME, "global_flash"))
        )
        
        # Check save result
        messages = self.driver.find_elements(By.CLASS_NAME, "global_flash")
        for msg in messages:
            if msg.is_displayed():
                self.logger.info(f"Save result: {msg.text}")
                return "saved" in msg.text.lower()
        
        return False

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
