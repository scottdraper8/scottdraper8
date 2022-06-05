# DEPENDENCIES
# ---------------------------------------------------------------------------------------------- #
import os
import time
import json
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
# ---------------------------------------------------------------------------------------------- #


# CONFIG EMAIL CAPABILITIES
# ---------------------------------------------------------------------------------------------- #
def send_email(subject, body):
    sender = E_U_NAME
    receivers = ['admin@scottdraper.io']
    message = f'''
    From: Bot Draper <{E_U_NAME}>
    To: Scott Draper <{E_U_NAME}>
    Subject: {subject}

    {body}
    '''

    try:
        smtp_server = smtplib.SMTP_SSL('hs1.name.tools', 465)
        smtp_server.ehlo()
        smtp_server.login(E_U_NAME, E_PASS_KEY)
        smtp_server.sendmail(sender, receivers, message)
        smtp_server.close()
    except Exception as ex:
        print ('Email was not delivered:', '\n', ex)
# ---------------------------------------------------------------------------------------------- #


# CHROMEDRIVER & ENV CONFIGS
# ---------------------------------------------------------------------------------------------- #
opts = Options()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument("--start-maximized")
opts.add_argument("--window-size=1920,1080")
opts.add_argument('--disable-dev-shm-usage')
if os.environ.get('ON_HEROKU'):
    opts.add_argument('--headless')
    opts.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    E_U_NAME = os.environ.get('E_U_NAME')
    G_U_NAME = os.environ.get('G_U_NAME')
    E_PASS_KEY = os.environ.get('E_PASS_KEY')
    G_PASS_KEY = os.environ.get('G_PASS_KEY')
else:
    opts.binary_location = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    E_U_NAME = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['email']['u']
    G_U_NAME = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['github']['u']
    E_PASS_KEY = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['email']['p']
    G_PASS_KEY = json.load(open(f'{os.path.dirname(os.path.realpath(__file__))}\\credentials.json'))['github']['p']
# ---------------------------------------------------------------------------------------------- #
opts.add_argument('--headless') #TODO remove after development


# LAUNCH CHROMEDRIVER
# ---------------------------------------------------------------------------------------------- #
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=opts)
driver.get('https://app.daily.dev/')
if not os.environ.get('ON_HEROKU'):
    driver.set_window_position(-1000, 0)
    driver.maximize_window()
# ---------------------------------------------------------------------------------------------- #


# LOG IN TO DAILY.DEV VIA GITHUB
# ---------------------------------------------------------------------------------------------- #
WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='//span[text()="Access all features"]'))
driver.find_element(by=By.XPATH, value='//span[text()="Access all features"]').click()
WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='(//button/span)[13]'))
driver.find_element(by=By.XPATH, value='(//button/span)[13]').click()
WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='//input[@name="login"]'))
driver.find_element(by=By.XPATH, value='//input[@name="login"]').send_keys(G_U_NAME)
driver.find_element(by=By.XPATH, value='//input[@type="password"]').send_keys(G_PASS_KEY)
driver.find_element(by=By.XPATH, value='//input[@type="submit"]').click()

# overcome GitHub's device verification
try:
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='//img[@alt="scottdraper\'s profile"]'))
except:
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='//h1[@data-test-selector="github-mobile-challenge"]'))
    auth_code = driver.find_element(by=By.XPATH, value='//h1[@data-test-selector="github-mobile-challenge"]').text
    send_email('GitHub Auth Code', f'''
        Your Daily.dev auto-article-reader is attempting to login to Daily.dev via GitHub. 
        Enter the following code into your GitHub mobile app: {auth_code} \n
        This code expires in 10 minutes.
    ''')
    WebDriverWait(driver, timeout=600).until(lambda d: d.find_element(by=By.XPATH, value='//img[@alt="scottdraper\'s profile"]'))
# ---------------------------------------------------------------------------------------------- #


driver.quit()
