from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import sqlite3
import random
import datetime

driver = webdriver.Chrome()
topic = "laptop"
last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
driver.maximize_window()
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
    cursor.execute('DROP TABLE IF EXISTS amazon')
    
    #  CREATE a fresh, empty table
    cursor.execute('''
        CREATE TABLE amazon (
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

number_of_items = 0
conn = setup_db() #establish connection to database
conn.close()
action = ActionChains(driver)

# Program Starts
for page in range(1, 4):
    
    action.move_by_offset(random.randint(10, 100), random.randint(10, 100)).perform()
    driver.get(f"https://www.amazon.com/s?k={topic}&page={page}&crid=2030M7N4CDAN5&sprefix=lapt%2Caps%2C379&ref=nb_sb_noss_2")
    
    random_human_scroll(driver)
    time.sleep(random.randint(2,5)) # make sur dirver open properly before we start to find elements
    items = driver.find_elements(By.CLASS_NAME, "puis-card-container") # find elements with class name "puis-card-container" and 
                                                                        #store them in a list called items. in this case a full card of a product 
                                                                        # #has a class beignning with puis-card-container.
    for i,item in enumerate(items[:40], start=0): #Run loop for each item in the items list items (1 product card)
        number_of_items += 1
        print("\n----------Item number: ", number_of_items,"----------\n")
        item_html = item.get_attribute("outerHTML") # get html of the item
        
        soup = BeautifulSoup(item_html, "html.parser") # parse the html with beautiful soup
        #extract Name
        try:
            name = soup.find("h2").text
        except:
            name = None

            
        #extract Price
  
        try:
            
            raw_price = soup.find("span", class_="a-price-whole").text
            

            clean_price = raw_price.replace("PKR", "").replace(",", "").replace(".", "").strip()
            

            price = int(clean_price)

        except:
            try:
                secondary_box = soup.find("div", {"data-cy": "secondary-offer-recipe"})
                raw_price = secondary_box.find("span", class_="a-color-base").text
                
                clean_price = raw_price.replace("PKR", "").replace(",", "").replace(".", "").strip()
                price = int(clean_price)
            except:
                price = None

        #extract Rating    
        try:
            full_rating = soup.find("span", class_="a-icon-alt").text
            rating = full_rating.split()[0]
            rating = float(rating)
        except:
            rating = None

        #extract buys
        try:
            buys = soup.find("span", class_="a-size-mini puis-normal-weight-text s-underline-text").text
            buys = buys.replace('(','') #remove parentheses from buys if they exist
            buys = buys.replace(')','')
            if "K" in buys:
                buys = buys.replace("K","")
                buys = float(buys) * 1000
                buys = int(buys)
        except:
            buys = None

        #extract link
        try: 
            link = soup.find("a", class_="a-link-normal")["href"]
            link = "https://www.amazon.com" + link
        except: 
            link = None

        website = "amazon"
        print("Name: ", name)
        print("Price: ", price)
        print("Rating: ", rating)  
        print("Buys: ", buys)
        print("Link: ", link)
        print("Website: ", website)
    
        


        #insert data into database
        conn = sqlite3.connect("market_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO amazon (name, price, rating, buys, link, website) VALUES (?, ?, ?, ?, ?, ?)", (name, price, rating, buys, link, website))
        conn.commit()
        
        

driver.quit()

