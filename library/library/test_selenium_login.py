import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from authentication.models import CustomUser


class LoginLogoutSeleniumTest(StaticLiveServerTestCase):
    """
    StaticLiveServerTestCase starts a Django test server in the background,
    so Selenium can open a real browser and interact with the pages.
    """

    @classmethod
    def setUpClass(cls):
        """Runs ONCE before all tests — opens the browser."""
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,800")

        cls.driver = webdriver.Chrome(options=chrome_options)

        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Runs ONCE after all tests — closes the browser."""
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """
        Runs before EACH test method.
        Creates a test user in the database that we can log in with.
        """
        self.test_email = "testuser@example.com"
        self.test_password = "SecurePass123!"
        self.test_first_name = "Test"
        self.test_last_name = "User"

        self.user = CustomUser.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name=self.test_first_name,
            last_name=self.test_last_name,
            is_active=True,
        )

    # ==================================================================
    # TEST 1: Log in with valid credentials, then log out
    # ==================================================================
    def test_valid_login_and_logout(self):
        """
        Scenario:
          1. Open the login page
          2. Enter valid email and password
          3. Click Login
          4. Verify: user is logged in
          5. Click Logout
          6. Verify: user is logged out 
        """
        driver = self.driver
        time.sleep(5)

        driver.get(f"{self.live_server_url}/login/")
        time.sleep(5)  

        self.assertIn("Login", driver.title)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.clear()
        email_field.send_keys(self.test_email)

        password_field.clear()
        password_field.send_keys(self.test_password)
        time.sleep(5)

        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
        login_button.click()
        time.sleep(5)

        self.assertNotIn("/login/", driver.current_url,
                         "Should be redirected away from login page after successful login")

        page_source = driver.page_source
        self.assertIn("Logout", page_source,
                      "Logout link should be visible after login")

        self.assertIn(self.test_first_name, page_source,
                      "User's first name should be visible in the nav bar")

        nav = driver.find_element(By.CSS_SELECTOR, "nav")
        nav_links = nav.find_elements(By.TAG_NAME, "a")
        nav_link_texts = [link.text for link in nav_links]
        self.assertNotIn("Login", nav_link_texts,
                         "Login link should NOT be visible when user is logged in")

        print("✓ User successfully logged in")

        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        logout_link.click()
        time.sleep(5)

        driver.get(f"{self.live_server_url}/")
        time.sleep(5)

        # DEBUG: let's see what the nav actually contains
        print("DEBUG current URL:", driver.current_url)
        print("DEBUG page title:", driver.title)
        nav = driver.find_element(By.CSS_SELECTOR, "nav")
        print("DEBUG nav text:", nav.text)

        nav = driver.find_element(By.CSS_SELECTOR, "nav")
        nav_links = nav.find_elements(By.TAG_NAME, "a")
        nav_link_texts = [link.text for link in nav_links]

        self.assertIn("Login", nav_link_texts,
                      "Login link should be visible after logout")
        self.assertNotIn("Logout", nav_link_texts,
                         "Logout link should NOT be visible after logout")

        print("✓ User successfully logged out")

    # ==================================================================
    # TEST 2: Login with INVALID credentials
    # ==================================================================
    def test_invalid_login(self):
        """
        Scenario:
          1. Open the login page
          2. Enter wrong email and password
          3. Click Login
          4. Verify: still on login page with error message
        """
        driver = self.driver

        driver.get(f"{self.live_server_url}/login/")
        time.sleep(5)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.clear()
        email_field.send_keys("wrong@email.com")

        password_field.clear()
        password_field.send_keys("WrongPassword123")
        time.sleep(5)

        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
        login_button.click()
        time.sleep(5)

        self.assertIn("/login/", driver.current_url,
                      "Should remain on login page after invalid credentials")

        error_div = driver.find_element(By.CSS_SELECTOR, "div.errors")
        self.assertTrue(error_div.is_displayed(),
                        "Error message should be visible")

        error_text = error_div.text
        self.assertIn("Invalid email or password", error_text,
                      "Error message should inform about invalid credentials")

        nav = driver.find_element(By.CSS_SELECTOR, "nav")
        nav_links = nav.find_elements(By.TAG_NAME, "a")
        nav_link_texts = [link.text for link in nav_links]
        self.assertNotIn("Logout", nav_link_texts,
                         "Logout should NOT appear — user is not logged in")

        print("✓ Invalid login correctly rejected with error message")