from backend.database import set_query_status, get_query_status, save_products, get_cached_products

print("Starting Supabase connection tests...\n")

# 1. Test Query Status Insert/Update
print("1. Testing set_query_status...")
set_query_status("test-query", "success")
print("Query status set successfully.")

# 2. Test Query Status Retrieve
print("\n2. Testing get_query_status...")
status, last_scraped = get_query_status("test-query")
print(f"Retrieved status: '{status}', last_scraped: {last_scraped}")

# 3. Test Products Save
print("\n3. Testing save_products...")
mock_products = [
    {
        "name": "Super Fast Test Laptop 2026",
        "price": 149999.0,
        "rating": 4.7,
        "buys": 50,
        "link": "https://priceoye.pk/laptops/test-laptop",
        "image_url": "https://images.priceoye.pk/test-laptop-270x270.webp",
        "website": "priceoye"
    }
]
save_products("test-query", mock_products)
print("Products saved successfully.")

# 4. Test Products Retrieve
print("\n4. Testing get_cached_products...")
cached_items = get_cached_products("test-query")
print("Retrieved cached products:")
for p in cached_items:
    print(f" - Name: {p['name']}")
    print(f" - Price: {p['price']}")
    print(f" - Rating: {p['rating']}")
    print(f" - Buys: {p['buys']}")
    print(f" - Link: {p['link']}")
    print(f" - Image URL: {p['image_url']}")
    print(f" - Website: {p['website']}")

print("\nConnection test completed successfully!")
