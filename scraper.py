from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import os

FILE = "lalitpur_pharmacies.xlsx"

options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--incognito")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

data = []
names_seen = set()

if os.path.exists(FILE):
    old_df = pd.read_excel(FILE)
    data = old_df.to_dict('records')
    names_seen = set(old_df["Name"].astype(str))
    print("Loaded:", len(data))

def save():
    while True:
        try:
            pd.DataFrame(data).to_excel(FILE, index=False)
            print("Saved:", len(data))
            break
        except PermissionError:
            input("Close Excel file and press ENTER...")

keywords = [
    "pharmacy","medical","chemist","drug store",
    "औषधि पसल","फार्मेसी","medical hall"
]

areas = [
    "Jawalakhel Lalitpur","Lagankhel Lalitpur","Satdobato Lalitpur",
    "Gwarko Lalitpur","Imadol Lalitpur","Balkumari Lalitpur",
    "Nakhu Lalitpur","Sunakothi Lalitpur","Tikathali Lalitpur",
    "Dhapakhel Lalitpur","Kumaripati Lalitpur","Pulchowk Lalitpur",
    "Mangalbazar Lalitpur","Godawari Lalitpur","Chapagaun Lalitpur",
    "Thecho Lalitpur","Thaiba Lalitpur","Harisiddhi Lalitpur"
]

new_found = 0

for area in areas:
    for key in keywords:

        search = f"{key} {area}"
        print("\nSearching:", search)

        driver.get("https://www.google.com/maps/search/" + search.replace(" ","+"))
        time.sleep(2)

        try:
            feed = driver.find_element(By.CSS_SELECTOR,'div[role="feed"]')
        except:
            continue

        for _ in range(15):
            driver.execute_script("arguments[0].scrollTop += 2000", feed)
            time.sleep(0.5)

        places = driver.find_elements(By.CSS_SELECTOR,"a.hfpxzc")
        links = list(set([p.get_attribute("href") for p in places if p.get_attribute("href")]))

        for link in links[:30]:

            driver.get(link)
            time.sleep(1)

            try:
                name = driver.find_element(By.TAG_NAME,"h1").text.strip()
            except:
                continue

            if name in names_seen or name == "":
                continue

            keywords_filter = ["pharmacy","pharma","medical","chemist","drug","औषधि"]

            if not any(x in name.lower() for x in keywords_filter):
                continue

            page = driver.page_source
            numbers = list(set(re.findall(r'\b(98\d{8}|97\d{8}|01\d{7})\b', page)))
            phone = numbers[0] if numbers else "Not Found"

            print(len(data)+1, name, phone)

            data.append({
                "Name": name,
                "Contact Number": phone,
                "Source": "Google Maps",
                "Link": link
            })

            names_seen.add(name)
            new_found += 1

            if len(data) % 10 == 0:
                save()

save()

print("\nNew added:", new_found)
print("Final total:", len(data))

driver.quit()
