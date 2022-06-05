# DEPENDENCIES
# ---------------------------------------------------------------------------------------------- #
import os
import sys
import time
import json
import smtplib
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
user_agent = UserAgent().random
opts.add_argument('--no-sandbox')
opts.add_argument('--log-level=3')
opts.add_argument('--disable-gpu')
opts.add_argument("--start-maximized")
opts.add_argument("--window-size=1920,1080")
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument(f'user-agent={user_agent}')
if os.environ.get('ON_HEROKU'):
    opts.add_argument('--headless')
    opts.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    E_U_NAME = os.environ.get('E_U_NAME')
    G_U_NAME = os.environ.get('G_U_NAME')
    E_PASS_KEY = os.environ.get('E_PASS_KEY')
    G_PASS_KEY = os.environ.get('G_PASS_KEY')
else:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    opts.binary_location = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    E_U_NAME = json.load(open(f'{parent_dir}\\credentials.json'))['email']['u']
    G_U_NAME = json.load(open(f'{parent_dir}\\credentials.json'))['github']['u']
    E_PASS_KEY = json.load(open(f'{parent_dir}\\credentials.json'))['email']['p']
    G_PASS_KEY = json.load(open(f'{parent_dir}\\credentials.json'))['github']['p']
# ---------------------------------------------------------------------------------------------- #
opts.add_argument('--headless') #TODO remove after development


# LAUNCH CHROMEDRIVER
# ---------------------------------------------------------------------------------------------- #
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=opts)
driver.get('https://app.daily.dev/')
# ---------------------------------------------------------------------------------------------- #


# LOG IN TO DAILY.DEV VIA GITHUB
# ---------------------------------------------------------------------------------------------- #
try:
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
        send_email('GitHub Auth Code', 
            f'''Your Daily.dev Auto Article Reader is attempting to login to Daily.dev via GitHub. 
            Enter the following code into your GitHub mobile app: {auth_code} \n
            This code expires in 10 minutes.''')
        WebDriverWait(driver, timeout=600).until(lambda d: d.find_element(by=By.XPATH, value='//img[@alt="scottdraper\'s profile"]'))
except Exception as e:
    send_email('Daily.dev Auto Article Reader Failure', 
        f'''Your Daily.dev Auto Article Reader was unable to login to Daily.dev. 
        Error Message:\n{e}''')
    driver.quit()
    sys.exit()
# ---------------------------------------------------------------------------------------------- #


# COLLECT ARTICLES TO READ
# ---------------------------------------------------------------------------------------------- #
article_urls = []
try:
    driver.get('https://app.daily.dev/my-feed')
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.XPATH, value='//img[@alt="scottdraper\'s profile"]'))
    no_change_count = 0
    while len(article_urls) < 300:
        if no_change_count == 1:
            print(f'Collected {len(article_urls)} articles')
        for url in driver.find_elements(by=By.XPATH, value='//article/a'):
            if url.get_attribute('href') not in article_urls and url.get_attribute('href').__contains__('api.daily.dev'):
                article_urls.append(url.get_attribute('href'))
                no_change_count = 0
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        no_change_count += 1
        if no_change_count == 5:
            break
except Exception as e:
    send_email('Daily.dev Auto Article Reader Failure', 
        f'''Your Daily.dev Auto Article Reader was unable to collect the designated number of articles to read.
        {len(article_urls)} of 300 articles were collected. 
        Error Message:\n{e}''')
    driver.quit()
    sys.exit()
# ---------------------------------------------------------------------------------------------- #


# READ COLLECTED ARTICLES
# ---------------------------------------------------------------------------------------------- #
try:
    [driver.execute_script(f'window.open("about:blank", "tab{x}");') for x in range(0, 21)]
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    for i, url in enumerate(article_urls):
        if i % 20 == 0 and i > 0:
            print(f'Reading articles {i - 20} to {i} of {len(article_urls)}...')
            current_urls = [article_urls[i] for i in range(i - 20, i + 1)]
            for x, link in enumerate(current_urls):
                driver.switch_to.window(f'tab{x}')
                driver.get(link)
        elif i % 20 != 0 and i + 20 > len(article_urls):
            print(f'Reading articles {i} to {len(article_urls)} of {len(article_urls)}...')
            current_urls = [article_urls[i] for i in range(i, len(article_urls))]
            for x, link in enumerate(current_urls):
                driver.switch_to.window(f'tab{x}')
                driver.get(link)
            break
except Exception as e:
    send_email('Daily.dev Auto Article Reader Failure', 
        f'''Your Daily.dev Auto Article Reader was unable to read all the collected articles.
        Error Message:\n{e}''')
    driver.quit()
    sys.exit()
# ---------------------------------------------------------------------------------------------- #


# FINISH AND REPORT
# ---------------------------------------------------------------------------------------------- #
send_email('Daily.dev Auto Article Reader Success', 
        f'Your Daily.dev Auto Article Reader collected and read a total of {len(article_urls)} articles. Great work!')
driver.quit()
# ---------------------------------------------------------------------------------------------- #