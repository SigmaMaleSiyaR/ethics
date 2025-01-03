from flask import Flask, jsonify
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time

app = Flask(__name__)

# Function to get the Selenium WebDriver
def get_driver():
    options = Options()
    options.binary_location = "/opt/google-chrome/chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--remote-debugging-port=9222")  # Add remote debugging port
    options.add_argument("--disable-gpu")  # Disable GPU usage
    options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
    service = Service("/app/chromedriver")
    return webdriver.Chrome(service=service, options=options)

    options = Options()
    options.binary_location = "/opt/google-chrome/chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service("/app/chromedriver")  # Update ChromeDriver path
    return webdriver.Chrome(service=service, options=options)

# Function to parse the status of the user
def parse_all_users_status(page_text):
    lines = page_text.split("\n")
    users_status = []
    ignored_keywords = ["Note...", "Messages", "Requests", "Your messages", "Send private photos", "Reacted", "ago", "·", "1y", "36w"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Identify valid user names by excluding common ignored keywords
        if line and not any(keyword in line for keyword in ignored_keywords):
            if not line.startswith("Active") and "Active" not in lines[i - 1] if i > 0 else True:
                user_status = {"user": line, "status": "No status found"}
                # Check the next lines for active or last active status
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "Active now" in lines[j]:
                        user_status["status"] = "Active now"
                        break
                    elif "Active" in lines[j]:
                        user_status["status"] = lines[j].strip()
                        break
                users_status.append(user_status)
        i += 1

    return users_status

# Function to check active status on Instagram
def check_active_status(username, password, target_user):
    driver = get_driver()
    try:
        driver.get("https://www.instagram.com")
        time.sleep(3)

        # Log in
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys("\n")
        time.sleep(5)

        # Navigate to messages
        driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(5)

        # Dismiss notification pop-up
        try:
            not_now_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now_button.click()
            time.sleep(2)
        except:
            pass

        # Wait for messages to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='presentation']"))
        )

        # Get the page text
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Parse and find the user status
        return page_text
    except Exception as e:
        return {"error": str(e)}
    finally:
        time.sleep(5)
        driver.quit()

@app.route('/')
def home():
    username = "nscc_bitw"
    password = "nscc_socials@123" # Replace with your Instagram password
    target_user = "Chaitanya Rawat"  # Replace with the display name of the target user
    result = check_active_status(username, password, target_user)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
