from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import sqlite3
import random

driver = webdriver.Chrome()
topic = "laptop"
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
item_number = 0


def random_human_scroll(driver):
    # Get the current total height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    
    # We will scroll in 4 to 8 random 
    num_bursts = random.randint(2,4)
    
    for _ in range(num_bursts):
        # Determine how far to scroll in this specific burst
        # (Usually 1/8th to 1/4th of the page)
        step = random.randint(300, 800)
        current_position += step
        
        # Perform the scroll
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        
        # "Micro-pauses" to simulate a human eye scanning the screen
        time.sleep(random.uniform(0.5, 2.0))
        
        # Occasional "Micro-scroll up" (very human-like behavior)
        if random.random() < 0.2:  # 20% chance to scroll back up slightly
            current_position -= random.randint(50, 150)
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.5)

    # Finally, scroll to the absolute bottom to ensure "Next" button is visible
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  


def setup_db():
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    
    # DELETEs the old table (overwriting)
    cursor.execute('DROP TABLE IF EXISTS daraz')
    
    #  CREATE a fresh, empty table
    cursor.execute('''
        CREATE TABLE daraz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            rating REAL,
            buys INTEGER,
            link TEXT,
            website TEXT
        )
    ''')
    conn.commit()
    return conn


conn = setup_db() #establish connection to database
conn.close()


# Program Starts--------------------------------------------------

driver.maximize_window()
for page in range(1, 4):
    time.sleep(random.randint(2,4)) # make sur dirver open properly before we start to find elements
    random_human_scroll(driver)
    driver.get(f"https://www.daraz.pk/catalog/?page={page}&q={topic}")
    items = driver.find_elements(By.CLASS_NAME, "buTCk")
    for i in items:
        item_number += 1
        print("\n----------Item number: ", item_number,"----------\n")
        item_html = i.get_attribute("outerHTML") # get html of the item
        soup = BeautifulSoup(item_html, "html.parser") # parse the html with beautiful soup
        #extract Name
        try:
            name = soup.find("div", class_="RfADt").text
        except:
            name = None


        #extract link
        try:
            tag = soup.find("a", href=True)
            if tag:
                link = "https:" + tag['href']
            else:
                link = None
        except:
            link = None


        #extract price
        try: 
            raw_price = soup.find("span", class_="ooOxS").text
            raw_price = raw_price.replace("Rs","").replace(",","").replace(".","").strip()
            price = int(raw_price)
        except:
            price = None


        #extract rating
        try:
            # Find the container div
            rating_container = soup.find("div", class_="mdmmT")
            
            if rating_container:
                # Find all <i> tags that have the Full Star "Dy1nx" class
                # We use a partial match because 'Dy1nx' is the unique identifier
                full_stars = rating_container.find_all("i", class_="Dy1nx")
                
                #count the number of full stars to determine the rating
                rating = len(full_stars)
                rating = float(rating) #convert rating to float for consistency with other scrapers
            else:
                rating = None
        except:
            rating = None

        #extract buys
        try:
            buys = soup.find("span", class_="_1cEkb").text
            if "sold" in buys:
                buys = buys.replace("sold","").strip()
                
            
            else:
                buys = buys.strip()
            if 'K' in buys:
                buys = buys.replace("K","")
                buys = float(buys) * 1000
                buys = int(buys)
            buys = int(buys)
       
        except:
            buys = None

        website = "daraz"
        print("Name: ", name)
        print("Price: ", price)
        print("Rating: ", rating)
        print("Buys: ", buys)
        print("Link: ", link)
        print("Website: ", website)

        #insert data into database
        conn = sqlite3.connect("market_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO daraz (name, price, rating, buys, link, website) VALUES (?, ?, ?, ?, ?, ?)", (name, price, rating, buys, link, website))
        conn.commit()


driver.quit()