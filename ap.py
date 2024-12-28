from flask import Flask, jsonify, request
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import re
from datetime import datetime, timedelta

class InstagramStatusParser:
    def __init__(self):
        self.ignored_keywords = {
            "Note...", "Messages", "Requests", "Your messages", 
            "Send private photos", "Send message", "Your note",
            "ago", "·", "Active", "You:", "Reacted"
        }

    def _get_time_weight(self, last_seen: str) -> int:
        """
        Convert last seen status to a numerical weight for sorting.
        Higher weight means more recent activity.
        """
        if not last_seen or last_seen == "Last seen unknown":
            return 0
        
        last_seen = last_seen.lower()
        
        if "active now" in last_seen:
            return 10000
        
        match = re.search(r'active (\d+)([hmw])', last_seen)
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'm':
                return 9000 - number  # Within hour
            elif unit == 'h':
                return 8000 - (number * 60)  # Within day
            elif unit == 'w':
                return 7000 - (number * 24 * 60)  # Within month
            
        return 0

    def _is_timestamp(self, text: str) -> bool:
        """Check if the text is a timestamp pattern."""
        timestamp_patterns = [
            r'\d+\s*(minutes?|hours?|days?|weeks?|months?|years?)\s*ago',
            r'\d+[hwmy]\s*ago',
            r'a year ago',
            r'about an hour ago',
            r'^\d+\s*(minutes?|hours?|days?|weeks?|months?|years?)$',
            r'^\d+[hwmy]$'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in timestamp_patterns)

    def _clean_time(self, time_str: str) -> str:
        """Clean and standardize time strings."""
        time_str = time_str.strip().lower()
        if "active now" in time_str:
            return "Active now"
        match = re.search(r'active (\d+[hwmy])', time_str, re.IGNORECASE)
        if match:
            return f"Active {match.group(1)}"
        return time_str

    def _is_valid_username(self, text: str, own_username: str) -> bool:
        """Check if the text is a valid username."""
        text = text.strip()
        return (
            text and
            text != own_username and
            not self._is_timestamp(text) and
            not any(keyword in text for keyword in self.ignored_keywords) and
            not text.startswith('Active') and
            not text.startswith('You:') and
            not text.startswith('Reacted')
        )

    def _get_message_weight(self, message: str) -> int:
        """
        Get weight for message recency.
        Custom messages get higher weight than default or reaction messages.
        """
        if message == "No recent messages":
            return 0
        elif message == "Reacted to a message":
            return 50
        else:
            return 100

    def parse_instagram_status(self, text: str, own_username: str = "") -> dict:
        """Parse Instagram chat list into user status information."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        users_data = {}
        i = 0
        
        while i < len(lines):
            current_line = lines[i]
            
            if self._is_valid_username(current_line, own_username):
                username = current_line
                
                if username not in users_data:
                    users_data[username] = {
                        "username": username,
                        "last_seen": "Last seen unknown",
                        "last_message": "No recent messages"
                    }
                
                look_ahead = min(i + 3, len(lines))
                for j in range(i + 1, look_ahead):
                    next_line = lines[j].strip()
                    
                    if "active" in next_line.lower():
                        users_data[username]["last_seen"] = self._clean_time(next_line)
                    elif next_line.startswith("You:"):
                        users_data[username]["last_message"] = next_line[4:].strip()
                    elif "Reacted" in next_line:
                        users_data[username]["last_message"] = "Reacted to a message"
            
            i += 1

        # Convert to list and sort by activity and message recency
        users_list = list(users_data.values())
        users_list.sort(
            key=lambda x: (
                self._get_time_weight(x["last_seen"]),  # First priority: active status
                self._get_message_weight(x["last_message"])  # Second priority: message type
            ),
            reverse=True  # Sort in descending order (most recent first)
        )
        
        return {"users": users_list}

app = Flask(__name__)

def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(r"C:\Program Files\driver\chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

def check_active_status(username, password):
    driver = get_driver()
    try:
        driver.get("https://www.instagram.com")
        time.sleep(3)

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys("\n")
        time.sleep(5)

        driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(5)

        try:
            not_now_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now_button.click()
            time.sleep(2)
        except:
            pass

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='presentation']"))
        )

        page_text = driver.find_element(By.TAG_NAME, "body").text
        parser = InstagramStatusParser()
        return parser.parse_instagram_status(page_text, username)

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

@app.route('/')
def home():
    username = "rawat_chunnilal"
    password = "Bit#1234"
    result = check_active_status(username, password)
    return jsonify(result)

@app.route('/parse', methods=['POST'])
def parse_status():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        own_username = data.get('username', 'nscc_bitw')
        parser = InstagramStatusParser()
        parsed_data = parser.parse_instagram_status(data['text'], own_username)
        return jsonify(parsed_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)