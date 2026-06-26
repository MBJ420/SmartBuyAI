import os
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the root .env file
# Since database.py is inside backend/, we load the env file from one directory up
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize the Supabase client
# We check if keys are configured. If not, we log a warning but don't crash immediately 
# to allow easy environment debugging.
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY is missing in environmental variables. Please configure your .env file.")

def get_supabase_client() -> Client:
    """Returns the initialized Supabase client, raising an error if credentials aren't set."""
    global supabase
    if supabase is None:
        # Retry loading credentials in case they were added dynamically
        load_dotenv(dotenv_path=env_path)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            supabase = create_client(url, key)
            return supabase
        raise ValueError(
            "Supabase client is not initialized. Please ensure SUPABASE_URL and SUPABASE_KEY are defined in your .env file."
        )
    return supabase

def init_db():
    """
    Attempts to automatically initialize tables in your Supabase database 
    if the direct PostgreSQL connection string (SUPABASE_DB_URL) is provided.
    Otherwise, prints instructions for manual table creation.
    """
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print("\nNOTE: SUPABASE_DB_URL is not configured in your .env file.")
        print("To enable automatic table creation on startup, add SUPABASE_DB_URL to your .env.")
        print("Otherwise, ensure the following tables are created in your Supabase SQL Editor:\n")
        print("--- COPY AND RUN THIS IN SUPABASE SQL EDITOR ---")
        print("""
CREATE TABLE IF NOT EXISTS queries (
    query TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    last_scraped_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    name TEXT NOT NULL,
    price DOUBLE PRECISION,
    rating DOUBLE PRECISION,
    buys INTEGER,
    link TEXT,
    image_url TEXT,
    website TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
        """)
        print("------------------------------------------------\n")
        return

    try:
        import psycopg2
        print("Connecting to Supabase via Postgres to auto-initialize tables...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 1. Create queries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                query TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_scraped_at TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # 2. Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                name TEXT NOT NULL,
                price DOUBLE PRECISION,
                rating DOUBLE PRECISION,
                buys INTEGER,
                link TEXT,
                image_url TEXT,
                website TEXT,
                scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Supabase database tables checked and initialized successfully!")
    except Exception as e:
        print(f"Failed to auto-initialize tables in Supabase: {e}")

def get_query_status(query: str):
    """
    Checks if we have searched this query before and returns its status.
    Returns a tuple: (status, last_scraped_at) or (None, None) if never searched.
    """
    try:
        client = get_supabase_client()
        clean_query = query.lower().strip()
        
        response = client.table("queries").select("status, last_scraped_at").eq("query", clean_query).execute()
        
        if response.data and len(response.data) > 0:
            row = response.data[0]
            return row.get("status"), row.get("last_scraped_at")
    except Exception as e:
        print(f"Error querying status from Supabase for query '{query}': {e}")
    return None, None

def set_query_status(query: str, status: str):
    """Inserts or updates the scraping status of a search query in Supabase."""
    try:
        client = get_supabase_client()
        clean_query = query.lower().strip()
        # Using ISO-format UTC timestamp for Supabase timestamptz
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        client.table("queries").upsert({
            "query": clean_query,
            "status": status,
            "last_scraped_at": now
        }).execute()
    except Exception as e:
        print(f"Error setting status in Supabase for query '{query}': {e}")

def get_cached_products(query: str):
    """Fetches all cached products for a specific search query from Supabase."""
    try:
        client = get_supabase_client()
        clean_query = query.lower().strip()
        
        response = client.table("products").select("name, price, rating, buys, link, image_url, website").eq("query", clean_query).execute()
        
        products = []
        if response.data:
            for row in response.data:
                products.append({
                    "name": row.get("name"),
                    "price": row.get("price"),
                    "rating": row.get("rating"),
                    "buys": row.get("buys"),
                    "link": row.get("link"),
                    "image_url": row.get("image_url"),
                    "website": row.get("website")
                })
        return products
    except Exception as e:
        print(f"Error fetching cached products from Supabase for query '{query}': {e}")
        return []

def save_products(query: str, products_list: list[dict]):
    """
    Saves a list of scraped products into Supabase.
    It deletes any old cached products for this query first.
    """
    try:
        client = get_supabase_client()
        clean_query = query.lower().strip()
        
        # 1. Clear out any old product entries for this query
        client.table("products").delete().eq("query", clean_query).execute()
        
        # 2. Insert new products (if there are any)
        if products_list:
            rows_to_insert = []
            for p in products_list:
                rows_to_insert.append({
                    "query": clean_query,
                    "name": p.get("name"),
                    "price": float(p.get("price")) if p.get("price") is not None else None,
                    "rating": float(p.get("rating")) if p.get("rating") is not None else None,
                    "buys": int(p.get("buys")) if p.get("buys") is not None else None,
                    "link": p.get("link"),
                    "image_url": p.get("image_url"),
                    "website": p.get("website")
                })
            client.table("products").insert(rows_to_insert).execute()
            print(f"Saved {len(products_list)} products to Supabase for query '{query}'.")
    except Exception as e:
        print(f"Error saving products to Supabase for query '{query}': {e}")

# Initialize the database/tables immediately when database.py is loaded
init_db()
