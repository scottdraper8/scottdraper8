# DEPENDENCIES
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# CHROMEDRIVER CONFIGS
opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--disable-dev-shm-usage')
if os.environ.get('ON_HEROKU'):
    opts.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
else:
    opts.binary_location = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=opts)
driver.get('https://scottdraper.io')
print(driver.page_source)
driver.quit()
