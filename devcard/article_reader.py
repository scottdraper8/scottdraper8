# DEPENDENCIES
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# CHROMEDRIVER & ENV CONFIGS
opts = Options()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--disable-dev-shm-usage')
if os.environ.get('ON_HEROKU'):
    opts.add_argument('--headless')
    opts.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    U_NAME = os.environ.get('U_NAME')
    PASS_KEY = os.environ.get('PASS_KEY')
else:
    opts.binary_location = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    U_NAME = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['u']
    PASS_KEY = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['p']


# LAUNCH CHROMEDRIVER
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=opts)
driver.get('https://app.daily.dev/')
if not os.environ.get('ON_HEROKU'):
    driver.set_window_position(-1000, 0)
    driver.maximize_window()


# LOG IN TO DAILY.DEV VIA GITHUB
driver.find_element(by=By.XPATH, value='//span[text()="Access all features"]').click()
WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(by=By.XPATH, value='(//button/span)[13]'))
driver.find_element(by=By.XPATH, value='(//button/span)[13]').click()
WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(by=By.XPATH, value='//input[@name="login"]'))
driver.find_element(by=By.XPATH, value='//input[@name="login"]').send_keys(U_NAME)
driver.find_element(by=By.XPATH, value='//input[@type="password"]').send_keys(PASS_KEY)
driver.find_element(by=By.XPATH, value='//input[@type="submit"]').click()
WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(by=By.XPATH, value='//img[@alt="scottdraper\'s profile"]'))
# time.sleep(3)
driver.quit()
