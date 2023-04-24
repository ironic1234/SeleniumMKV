from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime
import time
import pandas as pd
from collections import Counter
import re

options = Options()
options.headless = True
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
service  = Service(executable_path="chromedriver.exe")
driver  = webdriver.Chrome(service=service, options=options)
pattern = r'^(.*)\s+price target (raised|lowered)\s+to\s+(.*)\s+from\s+(.*)\s+at\s+(.*)$'

driver.get("https://thefly.com/news.php")

for i in range(600):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

print(driver.page_source)

time.sleep(3)

articles = driver.find_elements(By.CLASS_NAME, "newsTitleLink")
dates = driver.find_elements(By.CLASS_NAME, "fechaConAnio")

count = 0
companiesfull = []
datesfull = []

for article in articles:
    print(article.get_attribute("textContent"))
    dateandtime = datetime.datetime.strptime(dates[count].get_attribute("textContent")[:8] + " " + dates[count].get_attribute("textContent")[8:], "%m/%d/%y %H:%M")
    age = (datetime.datetime.now() - dateandtime)
    if (age.total_seconds())/3600 <= 72:
        try:
            if re.search(pattern, article.get_attribute("textContent")) != None:
                companiesfull.append([re.search(pattern, article.get_attribute("textContent")).group(i) for i in range(1, 6)])
                datesfull.append(dates[count].get_attribute("textContent")[:8] + " " + dates[count].get_attribute("textContent")[8:])
        except:
            continue
    count += 1

raisedcompanies = []
loweredcompanies = []

for company in companiesfull:
    if company[1] == "raised":
        raisedcompanies.append(company[0])
    elif company[1] == "lowered":
        loweredcompanies.append(company[0])

df1 = pd.DataFrame({"Name" : dict(Counter(raisedcompanies)).keys(), "Count" : dict(Counter(raisedcompanies)).values()})

df2 = pd.DataFrame({"Name" : dict(Counter(loweredcompanies)).keys(), "Count" : dict(Counter(loweredcompanies)).values()})

df3 = pd.DataFrame({"Name" : [list[0] for list in companiesfull], "Raised/Lowered" : [list[1] for list in companiesfull], "To" : [list[2] for list in companiesfull], "From" : [list[3] for list in companiesfull], "Company" : [list[4] for list in companiesfull], "Date" : datesfull})


with pd.ExcelWriter(f"{input('What would you like to name the spreadsheet? ')}.xlsx") as writer:
    df1.to_excel(writer, sheet_name="Raised", index=False)
    df2.to_excel(writer, sheet_name="Lowered", index=False)
    df3.to_excel(writer, sheet_name="All", index=False)

driver.close()