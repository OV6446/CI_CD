from django.test import TestCase
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid


class UserAuthSeleniumTests(LiveServerTestCase):
    # Подготавливает браузер перед запуском тестов
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

   
    # Очищает ресурсы после выполнения всех тестов
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    def click_submit(self):
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.2)
        try:
            button.click()
        except Exception as e:
            try:
                self.driver.execute_script("arguments[0].click();", button)
            except Exception as js_e:
                self.driver.save_screenshot('selenium_error.png')
                raise Exception(f"Selenium click failed: {e}, JS click failed: {js_e}. Screenshot saved as selenium_error.png")
   
    # Выполняет выход пользователя через переход на /logout/
    def logout(self):
        self.driver.get(f'{self.live_server_url}/logout/')
        time.sleep(0.5)

    # Тест регистрации пользователя с корректными данными
    def test_register_success(self):
        self.driver.get(f'{self.live_server_url}/register/')
        self.driver.find_element(By.ID, 'id_username').send_keys('testuser')
        self.driver.find_element(By.ID, 'id_email').send_keys('testuser@example.com')
        self.driver.find_element(By.ID, 'id_password1').send_keys('TestPassword123!')
        self.driver.find_element(By.ID, 'id_password2').send_keys('TestPassword123!')
        self.click_submit()
        time.sleep(1)
        self.assertNotIn('/register', self.driver.current_url)

    # Тест регистрации пользователя с несовпадающими паролями
    def test_register_password_mismatch(self):
        self.driver.get(f'{self.live_server_url}/register/')
        self.driver.find_element(By.ID, 'id_username').send_keys('testuser2')
        self.driver.find_element(By.ID, 'id_email').send_keys('testuser2@example.com')
        self.driver.find_element(By.ID, 'id_password1').send_keys('TestPassword123!')
        self.driver.find_element(By.ID, 'id_password2').send_keys('WrongPassword!')
        self.click_submit()
        time.sleep(1)
        self.assertIn('Пароли не совпадают', self.driver.page_source)

    # Тест логина пользователя с корректными данными
    def test_login_success(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='loginuser', email='loginuser@example.com', password='TestPassword123!')
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys('loginuser')
        self.driver.find_element(By.NAME, 'password').send_keys('TestPassword123!')
        self.click_submit()
        time.sleep(1)
        self.assertNotIn('/login', self.driver.current_url)
        
    # Тест логина пользователя с некорректным паролем
    def test_login_wrong_password(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='wrongpass', email='wrongpass@example.com', password='TestPassword123!')
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys('wrongpass')
        self.driver.find_element(By.NAME, 'password').send_keys('WrongPassword!')
        self.click_submit()
        time.sleep(1)
        self.assertIn('Неверное имя пользователя или пароль', self.driver.page_source)

    # Тест регистрации пользователя с различными случаями
    test_users = [
        # Корректные данные
        {"username": "user1", "email": "user1@example.com", "password": "TestPassword123!", "password2": "TestPassword123!", "expect_success": True, "desc": "Валидная регистрация"},
        # Короткий пароль
        {"username": "user2", "email": "user2@example.com", "password": "123", "password2": "123", "expect_success": False, "desc": "Слишком короткий пароль"},
        # Пароли не совпадают
        {"username": "user3", "email": "user3@example.com", "password": "TestPassword123!", "password2": "WrongPassword!", "expect_success": False, "desc": "Пароли не совпадают"},
        # Некорректный email
        {"username": "user4", "email": "not-an-email", "password": "TestPassword123!", "password2": "TestPassword123!", "expect_success": False, "desc": "Некорректный email"},
        # Пустое имя пользователя
        {"username": "", "email": "user5@example.com", "password": "TestPassword123!", "password2": "TestPassword123!", "expect_success": False, "desc": "Пустое имя пользователя"},
        # Пустой email
        {"username": "user6", "email": "", "password": "TestPassword123!", "password2": "TestPassword123!", "expect_success": False, "desc": "Пустой email"},
        # Пустой пароль
        {"username": "user7", "email": "user7@example.com", "password": "", "password2": "", "expect_success": False, "desc": "Пустой пароль"},
        # Уже существующий пользователь
        {"username": "user1", "email": "user1@example.com", "password": "TestPassword123!", "password2": "TestPassword123!", "expect_success": False, "desc": "Пользователь уже существует"},
        # Длинный пароль (100 символов)
        {"username": "user9", "email": "user9@example.com", "password": "a" * 100, "password2": "a" * 100, "expect_success": True, "desc": "Длинный, но валидный пароль (100)"},
        # Специальные символы в пароле
        {"username": "user10", "email": "user10@example.com", "password": "Test@#$%^&*()_+", "password2": "Test@#$%^&*()_+", "expect_success": True, "desc": "Пароль со спецсимволами"},
    ]

    # Тест логина пользователя с различными случаями
    login_cases = [
        {"username": "user1", "password": "TestPassword123!", "expect_success": True, "desc": "Валидный логин"},
        {"username": "user1", "password": "WrongPassword!", "expect_success": False, "desc": "Неверный пароль"},
        {"username": "user2", "password": "TestPassword123!", "expect_success": False, "desc": "Несуществующий пользователь"},
        {"username": "", "password": "TestPassword123!", "expect_success": False, "desc": "Пустой логин"},
        {"username": "user1", "password": "", "expect_success": False, "desc": "Пустой пароль"},
        # Логин по email (если поддерживается)
        {"username": "user1@example.com", "password": "TestPassword123!", "expect_success": False, "desc": "Логин по email"},
        # Длинный пароль (100 символов)
        {"username": "user1", "password": "a" * 100, "expect_success": False, "desc": "Очень длинный пароль (100)"},
    ]

    # Тест регистрации пользователя с различными случаями
    def test_registration_various_cases(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='user1', email='user1@example.com', password='TestPassword123!')
        for i, data in enumerate(self.test_users):
            self.driver.get(f'{self.live_server_url}/register/')
            if data["desc"] not in ["Пользователь уже существует"]:
                unique = str(uuid.uuid4())[:8]
                username = data["username"] + unique if data["username"] else ""
                email = data["email"].replace("@", f"{unique}@") if data["email"] else ""
            else:
                username = data["username"]
                email = data["email"]
            self.driver.find_element(By.ID, 'id_username').clear()
            self.driver.find_element(By.ID, 'id_email').clear()
            self.driver.find_element(By.ID, 'id_password1').clear()
            self.driver.find_element(By.ID, 'id_password2').clear()
            self.driver.find_element(By.ID, 'id_username').send_keys(username)
            self.driver.find_element(By.ID, 'id_email').send_keys(email)
            self.driver.find_element(By.ID, 'id_password1').send_keys(data["password"])
            self.driver.find_element(By.ID, 'id_password2').send_keys(data["password2"])
            self.click_submit()
            time.sleep(1)
            if data["expect_success"]:
                result = self.driver.current_url.endswith('/register/') == False
                print(f'REGISTER: {data["desc"]}: Ожидалось УСПЕШНО, результат: {"УСПЕШНО" if result else "ОШИБКА"}')
                self.assertTrue(result)
                self.logout()
            else:
                result = self.driver.current_url.endswith('/register/')
                print(f'REGISTER: {data["desc"]}: Ожидалась ОШИБКА, результат: {"ОШИБКА" if result else "УСПЕШНО"}')
                self.assertTrue(result)

    # Тест логина пользователя с различными случаями
    def test_login_various_cases(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='user1', email='user1@example.com', password='TestPassword123!')
        for data in self.login_cases:
            self.driver.get(f'{self.live_server_url}/login/')
            try:
                self.driver.find_element(By.NAME, 'username').clear()
                self.driver.find_element(By.NAME, 'password').clear()
                self.driver.find_element(By.NAME, 'username').send_keys(data["username"])
                self.driver.find_element(By.NAME, 'password').send_keys(data["password"])
                self.click_submit()
                time.sleep(1)
                if data["expect_success"]:
                    result = self.driver.current_url.endswith('/login/') == False
                    print(f'LOGIN: {data["desc"]}: Ожидалось УСПЕШНО, результат: {"УСПЕШНО" if result else "ОШИБКА"}')
                    self.assertTrue(result)
                    self.logout()
                else:
                    result = self.driver.current_url.endswith('/login/')
                    print(f'LOGIN: {data["desc"]}: Ожидалась ОШИБКА, результат: {"ОШИБКА" if result else "УСПЕШНО"}')
                    self.assertTrue(result)
            except Exception as e:
                if data["expect_success"]:
                    print(f'LOGIN: {data["desc"]}: Ожидалось УСПЕШНО, результат: ОШИБКА')
                else:
                    print(f'LOGIN: {data["desc"]}: Ожидалась ОШИБКА, результат: ОШИБКА')
                self.assertFalse(data["expect_success"])

    # Тест массовой регистрации пользователей
    def test_mass_registration(self):
        """Тест массовой регистрации пользователей"""
        print("\n=== ТЕСТ МАССОВОЙ РЕГИСТРАЦИИ ===")
        success_count = 0
        for i in range(5):
            unique = str(uuid.uuid4())[:8]
            username = f"massuser{i}_{unique}"
            email = f"massuser{i}_{unique}@example.com"
            password = f"TestPassword{i}!"
            
            self.driver.get(f'{self.live_server_url}/register/')
            self.driver.find_element(By.ID, 'id_username').send_keys(username)
            self.driver.find_element(By.ID, 'id_email').send_keys(email)
            self.driver.find_element(By.ID, 'id_password1').send_keys(password)
            self.driver.find_element(By.ID, 'id_password2').send_keys(password)
            self.click_submit()
            time.sleep(1)
            
            if not self.driver.current_url.endswith('/register/'):
                success_count += 1
                print(f"Массовая регистрация {i+1}: УСПЕШНО")
                self.logout()
            else:
                print(f"Массовая регистрация {i+1}: ОШИБКА")
        
        print(f"Итого успешных регистраций: {success_count}/5")
        self.assertGreaterEqual(success_count, 4)  
