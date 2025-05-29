import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException



class TestResult:
    def __init__(self, name, status, message=""):
        self.name = name
        self.status = status
        self.message = message


class TestBlogspot:
    @pytest.fixture(scope="class")
    def driver_setup(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver
        driver.quit()

    @pytest.fixture(autouse=True)
    def setup(self, driver_setup):
        self.driver = driver_setup
        self.wait = WebDriverWait(self.driver, 10,
                                  ignored_exceptions=[NoSuchElementException, StaleElementReferenceException])
        self.results = []

    def wait_and_click(self, by, value, description=""):
        """Wait for element to be clickable and then click it"""
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            time.sleep(0.5)  
            element.click()
            time.sleep(0.5)  
            if description:
                self.results.append(TestResult(f"Click: {description}", "PASS"))
            return element
        except TimeoutException:
            self.driver.save_screenshot(f"error_click_{value}.png")
            if description:
                self.results.append(TestResult(f"Click: {description}", "FAIL", f"Element not clickable: {value}"))
            raise

    def wait_and_send_keys(self, by, value, text, description=""):
        """Wait for element to be visible, then send keys"""
        try:
            element = self.wait.until(EC.visibility_of_element_located((by, value)))
            element.clear()
            time.sleep(0.5)  
          
            for char in text:
                element.send_keys(char)
                time.sleep(0.05)  
            time.sleep(0.5)  
            if description:
                self.results.append(TestResult(f"Input: {description}", "PASS"))
            return element
        except TimeoutException:
            self.driver.save_screenshot(f"error_send_keys_{value}.png")
            if description:
                self.results.append(TestResult(f"Input: {description}", "FAIL", f"Element not visible: {value}"))
            raise

    def is_element_present(self, by, value, timeout=5):
        """Check if element exists on page"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def run_test_step(self, step_name, step_function, *args, **kwargs):
        """Run a test step and record the result"""
        try:
            step_function(*args, **kwargs)
            self.results.append(TestResult(step_name, "PASS"))
            return True
        except Exception as e:
            self.results.append(TestResult(step_name, "FAIL", str(e)))
            self.driver.save_screenshot(f"{step_name.replace(' ', '_')}_error.png")
            return False

    @pytest.mark.parametrize("step_name", [
        "Login as John",
        "Read and Comment on Blog",
        "Create Forum Post",
        "Navigate to About and Contact",
        "Update Profile",
        "Social Interactions",
        "Login as Moumita",
        "Blogger Operations",
        "Message Management",
        "Profile Update and Logout"
    ])
    def test_blogspot_steps(self, step_name):
        """Run individual test steps as separate test cases"""
        if step_name == "Login as John":
            
            self.driver.get("http://127.0.0.1:8000/")
            time.sleep(1)  

            # Login
            self.wait_and_click(By.LINK_TEXT, "Sign In", "Click Sign In button")
            self.wait_and_send_keys(By.ID, "username", "john", "Enter username")
            self.wait_and_send_keys(By.ID, "password", "112233", "Enter password")
            self.wait_and_click(By.CSS_SELECTOR, ".bg-blue-500", "Click login button")

            
            assert self.is_element_present(By.LINK_TEXT, "john"), "Login failed"

        elif step_name == "Read and Comment on Blog":
            
            self.wait_and_click(By.XPATH, '//*[@id="collapseMenu"]/div/ul/li[2]/a', "Click Read Blogs link")
            self.wait_and_click(By.XPATH, '/html/body/div/div[4]/div/div[2]/div[2]/div[2]/a', "Click Read More on a blog")

            
            comment_selectors = [
                (By.NAME, "content"),
                (By.ID, "content"),
                (By.CSS_SELECTOR, "textarea[name='content']"),
                (By.CSS_SELECTOR, ".comment-form textarea"),
                (By.CSS_SELECTOR, "form textarea")
            ]

            for selector in comment_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_send_keys(selector[0], selector[1], "This is nice", "Enter comment")
                    break
            else:
                self.driver.save_screenshot("comment_field_not_found.png")
                pytest.fail("Could not find comment field")

            
            if self.is_element_present(By.CSS_SELECTOR, ".mb-4:nth-child(1)"):
                self.driver.find_element(By.CSS_SELECTOR, ".mb-4:nth-child(1)").click()
                time.sleep(0.5)

            submit_selectors = [
                (By.CSS_SELECTOR, ".mt-3"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, ".comment-form button"),
                (By.CSS_SELECTOR, "form button")
            ]

            for selector in submit_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_click(selector[0], selector[1], "Submit comment")
                    break
            else:
                self.driver.save_screenshot("submit_button_not_found.png")
                pytest.fail("Could not find submit button")

        elif step_name == "Create Forum Post":
            
            self.wait_and_click(By.LINK_TEXT, "Forum", "Click Forum link")
            self.wait_and_click(By.LINK_TEXT, "New Post", "Click New Post button")

            
            self.wait_and_send_keys(By.ID, "title", "I need Help", "Enter post title")
            self.wait_and_send_keys(By.ID, "content", "I need help based on reach out new bloggers on this platform",
                                    "Enter post content")
            self.wait_and_click(By.CSS_SELECTOR, ".from-indigo-600", "Submit post")

            
            try:
                self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".bg-white:nth-child(1) > .p-6"))).click()
                time.sleep(0.5)
            except TimeoutException:
                if self.is_element_present(By.CSS_SELECTOR, ".post-container:first-child"):
                    self.wait_and_click(By.CSS_SELECTOR, ".post-container:first-child", "Click on post")
                else:
                    self.driver.save_screenshot("post_not_found.png")
                    pytest.fail("Could not find created post")

        elif step_name == "Navigate to About and Contact":
            
            self.wait_and_click(By.LINK_TEXT, "About", "Click About link")
            time.sleep(1)  

            
            self.wait_and_click(By.LINK_TEXT, "Contact", "Click Contact link")
            time.sleep(1)  

        elif step_name == "Update Profile":
            
            self.wait_and_click(By.LINK_TEXT, "john", "Click username link")

            
            self.wait_and_send_keys(By.NAME, "bio", "I love youtubeI love youtube I love coding", "Update bio")
            self.wait_and_click(By.CSS_SELECTOR, ".update-btn", "Click update button")

        elif step_name == "Social Interactions":
            
            self.wait_and_click(By.CSS_SELECTOR, ".text-teal-500", "Click social icon")
            self.wait_and_click(By.CSS_SELECTOR, ".fa-user-plus", "Click add user icon")
            self.wait_and_click(By.CSS_SELECTOR, ".open-message-modal", "Click message icon")
            self.wait_and_send_keys(By.NAME, "content", "You are great", "Enter message")
            self.wait_and_click(By.CSS_SELECTOR, ".px-6", "Send message")

        elif step_name == "Login as Moumita":
            
            self.wait_and_click(By.LINK_TEXT, "Logout", "Click Logout link")

            
            self.wait_and_click(By.LINK_TEXT, "Login as Blogger", "Click Login as Blogger")
            self.wait_and_send_keys(By.ID, "username", "moumita", "Enter username")
            self.wait_and_send_keys(By.ID, "password", "112233", "Enter password")
            self.wait_and_click(By.CSS_SELECTOR, ".bg-purple-500", "Click login button")

            
            assert self.is_element_present(By.LINK_TEXT, "moumita") or self.is_element_present(By.LINK_TEXT,
                                                                                               "Create Blog"), "Login as Moumita failed"

        elif step_name == "Blogger Operations":
            
            self.wait_and_click(By.LINK_TEXT, "Create Blog", "Click Create Blog link")
            time.sleep(1)  

            self.wait_and_click(By.LINK_TEXT, "My Blogs", "Click My Blogs link")
            time.sleep(1)  

            
            edit_selectors = [
                (By.CSS_SELECTOR, ".bg-white:nth-child(1) .flex > .bg-gradient-to-r > .fas"),
                (By.CSS_SELECTOR, ".edit-icon"),
                (By.CSS_SELECTOR, ".fa-edit"),
                (By.CSS_SELECTOR, "button[title='Edit']")
            ]

            for selector in edit_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_click(selector[0], selector[1], "Click edit button")
                    break
            else:
                self.driver.save_screenshot("edit_button_not_found.png")
                pytest.fail("Could not find edit button")

            
            title_element = self.wait.until(EC.visibility_of_element_located((By.NAME, "title")))
            title_element.clear()
            time.sleep(0.5)
            
            for char in "How to Make Science Relevant to Everyone of the worlds":
                title_element.send_keys(char)
                time.sleep(0.05)
            time.sleep(0.5)

            
            submit_selectors = [
                (By.CSS_SELECTOR, ".font-semibold"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, ".submit-btn"),
                (By.CSS_SELECTOR, "input[type='submit']")
            ]

            for selector in submit_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_click(selector[0], selector[1], "Submit edit")
                    break

        elif step_name == "Message Management":
            
            self.wait_and_click(By.LINK_TEXT, "Messages", "Click Messages link")
            time.sleep(1)  

            
            reply_selectors = [
                (By.CSS_SELECTOR, ".p-6:nth-child(1) .open-reply-modal"),
                (By.CSS_SELECTOR, ".reply-button"),
                (By.CSS_SELECTOR, "button[title='Reply']")
            ]

            for selector in reply_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_click(selector[0], selector[1], "Click reply button")

                    
                    if self.is_element_present(By.NAME, "reply", timeout=2):
                        self.wait_and_send_keys(By.NAME, "reply", "Thanks", "Enter reply")

                        
                        submit_selectors = [
                            (By.CSS_SELECTOR, ".py-2"),
                            (By.CSS_SELECTOR, "button[type='submit']"),
                            (By.CSS_SELECTOR, ".submit-btn")
                        ]

                        for submit_selector in submit_selectors:
                            if self.is_element_present(submit_selector[0], submit_selector[1], timeout=2):
                                self.wait_and_click(submit_selector[0], submit_selector[1], "Submit reply")
                                break
                    break

        elif step_name == "Profile Update and Logout":
            
            self.wait_and_click(By.LINK_TEXT, "Profile", "Click Profile link")

            
            bio_selectors = [
                (By.ID, "bio"),
                (By.NAME, "bio"),
                (By.CSS_SELECTOR, "textarea[name='bio']")
            ]

            for selector in bio_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_send_keys(selector[0], selector[1], "i love youtube", "Update bio")
                    break

            
            update_selectors = [
                (By.CSS_SELECTOR, ".px-4"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, ".update-btn")
            ]

            for selector in update_selectors:
                if self.is_element_present(selector[0], selector[1], timeout=2):
                    self.wait_and_click(selector[0], selector[1], "Submit profile update")
                    break

            
            self.wait_and_click(By.LINK_TEXT, "Logout", "Click Logout link")
            self.wait_and_click(By.LINK_TEXT, "Back to Home", "Click Back to Home")

        
        time.sleep(1)