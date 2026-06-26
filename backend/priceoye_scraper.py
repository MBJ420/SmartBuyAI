from bs4 import BeautifulSoup
import requests

def price_oye_scraper(query: str):
    url = f"https://priceoye.pk/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    # Fetch the content from the URL and parse it with BeautifulSoup
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    product_cards = soup.find_all("a", class_="product-card") 

    products = []

    for card in product_cards[:5]:
        print("\n----------Product Card----------\n")
        
        # extract Name
        try: 
            name = card["data-product-name"]
        except KeyError:
            name = None

        # extract link
        try: 
            link = card["href"]
        except:
            link = None

        # extract price
        try:
            price = card.find("div", class_="price-box p1 saving-hides").text
            price = price.replace("Rs", "")
            price = price.replace(",", "")
            price = float(price)
        except:
            price = None

        # extract rating
        try: 
            rating = card.find("span", class_="h6 bold").text
            rating = rating.strip()
            rating = float(rating)
        except:
            rating = None
        
        # extract buys
        try:
            buys = card.find("span", class_="rating-h7 bold").text
            buys = buys.strip()
            buys = int(buys)
        except:
            buys = None
            
        # extract image url
        try:
            image_url = card.find("amp-img", class_="product-thumbnail")["src"]
        except:
            try:
                image_url = card.find("img")["src"]
            except:
                image_url = None

        website = "priceoye"
        print("Name: ", name)
        print("Price: ", price)
        print("Rating: ", rating)  
        print("Buys: ", buys)
        print("Link: ", link)
        print("Image URL: ", image_url)
        print("Website: ", website)

        # Collect products in list of dicts
        products.append({
            "name": name,
            "price": price,
            "rating": rating,
            "buys": buys,
            "link": link,
            "image_url": image_url,
            "website": website
        })

    return products
