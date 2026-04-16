from bs4 import BeautifulSoup
import requests
url = "https://priceoye.pk/search?q=laptop"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

#Fetch the content from the URL and parse it with BeautifulSoup
response  = requests.get(url,headers=headers)
soup = BeautifulSoup(response.content,"html.parser")
product_cards = soup.find_all("a", class_="product-card") 

for card in product_cards[:5]:

    print("\n----------Product Card----------\n")
    #extract Name
    # in a single <a> tag wiht same class_="product-card", there are multiple attributes, to fetch a specific attribute we can use the following code:
    try: 
       #HTML code Line: <a class="product-card" data-product-id="11568" data-product-name="HP Laptop 15-FD0532NIA Intel Core i3-1315U 13th Gen (4GB-256GB)" href="https://priceoye.pk/laptops/hp/hp-laptop-15-fd0532nia-intel-core-i3-1315u-13th-gen-4gb-256gb">
        name = card["data-product-name"]

    except KeyError:
        name = None

    
    #extract link
    try: 
        link = card["href"]
    except:
        link = None

    
    #extract price
    try:
        price = card.find("div",class_="price-box p1 saving-hides").text
        price = price.replace("Rs","")
        price = price.replace(",","")
        price = float(price)
    except:
        price = None


    #extract rating

    try: 
        
        rating = card.find("span", class_="h6 bold").text
        rating = rating.strip()
        rating = float(rating)
    except:
        rating = None
    
    #extract buys
    try:
        buys = card.find("span", class_="rating-h7 bold").text
        buys = buys.strip()
        buys = int(buys)
        
    except:
        buys = None
        

    website = "priceoye"
    print("Name: ", name)
    print("Price: ", price)
    print("Rating: ", rating)  
    print("Buys: ", buys)
    print("Link: ", link)
    print("Website: ", website)
    
