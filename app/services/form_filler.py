import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.core.config import settings

logger = logging.getLogger(__name__)

def fill_form(extracted_data):
    """
    Fill out the Google Form with extracted data.

    Args:
        extracted_data: Dictionary containing extracted data from shipping documents

    Returns:
        bool: True if form was filled successfully, False otherwise
    """
    form_url = settings.FORM_URL
    
    # Set up Chrome options for headless operation
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        logger.info(f"Opening form at URL: {form_url}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(form_url)
        
        # Wait for the form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "whsOnd"))
        )
        
        # Map of field labels to their corresponding entry names in the form
        form_fields_mapping = {
            "Bill of lading number": {
                "type": "text",
                "entry_name": "entry.1641021725",
                "value": extracted_data.get("bill_of_lading_number", "")
            },
            "Container Number": {
                "type": "text",
                "entry_name": "entry.1026077439",
                "value": extracted_data.get("container_number", "")
            },
            "Consignee Name": {
                "type": "text",
                "entry_name": "entry.111572852",
                "value": extracted_data.get("consignee_name", "")
            },
            "Consignee Address": {
                "type": "textarea",
                "entry_name": "entry.1466739846",
                "value": extracted_data.get("consignee_address", "")
            },
            "Date": {
                "type": "date",
                "entry_name": "entry.1733712848",
                "value": format_date(extracted_data.get("date", ""))
            },
            "Line Items Count": {
                "type": "text",
                "entry_name": "entry.1492261839",
                "value": str(extracted_data.get("line_items_count", ""))
            },
            "Average Gross Weight": {
                "type": "text",
                "entry_name": "entry.605394403",
                "value": str(extracted_data.get("average_gross_weight", ""))
            },
            "Average Price": {
                "type": "text",
                "entry_name": "entry.1951650481",
                "value": str(extracted_data.get("average_price", ""))
            }
        }
        
        # Fill each field in the form
        for field_label, field_info in form_fields_mapping.items():
            try:
                if field_info["value"]:
                    logger.info(f"Filling field '{field_label}' with value: {field_info['value']}")
                    
                    # Find the field based on its type
                    if field_info["type"] == "text":
                        # Find the text input fields by their XPath using the field label
                        xpath = f"//div[contains(., '{field_label}')]/following::input[@type='text'][1]"
                        input_field = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        input_field.clear()
                        input_field.send_keys(field_info["value"])
                    
                    elif field_info["type"] == "textarea":
                        # Find textarea fields
                        xpath = f"//div[contains(., '{field_label}')]/following::textarea[1]"
                        textarea_field = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        textarea_field.clear()
                        textarea_field.send_keys(field_info["value"])
                    
                    elif field_info["type"] == "date":
                        # Handle date fields specially
                        if field_info["value"]:
                            # Google Forms expects dates in format dd/mm/yyyy
                            date_parts = field_info["value"].split("/")
                            
                            # For Google Forms date inputs we need to fill day, month, year separately
                            # Find the date input field
                            xpath = f"//div[contains(., '{field_label}')]/following::input[@type='date'][1]"
                            date_field = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, xpath))
                            )
                            
                            # Use JavaScript to set the date value directly
                            driver.execute_script(
                                "arguments[0].value = arguments[1]", 
                                date_field, 
                                field_info["value"]
                            )
            except Exception as e:
                logger.error(f"Error filling field {field_label}: {e}")
        
        # Find and click the submit button
        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Submit']"))
            )
            submit_button.click()
            
            # Wait for confirmation message that form was submitted
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your response has been recorded')]"))
            )
            logger.info("Form submitted successfully")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Error submitting form: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Unexpected error filling form: {e}")
        return False
        
    finally:
        # Clean up
        if driver:
            driver.quit()

def format_date(date_string):
    """
    Format date string to match expected format for the form (dd/mm/yyyy).
    
    Args:
        date_string: Date string in format MM/DD/YYYY or similar
        
    Returns:
        Formatted date string
    """
    if not date_string:
        return ""
    
    try:
        # Parse the date string
        parts = date_string.split('/')
        if len(parts) == 3:
            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
            # Format as YYYY-MM-DD for HTML date input
            return f"{year:04d}-{month:02d}-{day:02d}"
        return date_string
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        return date_string
