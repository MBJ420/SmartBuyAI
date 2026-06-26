from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import get_query_status, set_query_status, get_cached_products, save_products
from backend.priceoye_scraper import price_oye_scraper

app = FastAPI(title="SmartBuy AI Deal Finder API")

# Configure CORS so our frontend page can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrape_and_save_task(query: str):
    """Background task to run scrapers, save products, and update query status."""
    try:
        print(f"Background scraping started for query: {query}")
        
        # 1. Run the scraper
        scraped_products = price_oye_scraper(query)
        
        # 2. Save the results to SQLite cache
        save_products(query, scraped_products)
        
        # 3. Mark the search query status as 'success'
        set_query_status(query, "success")
        print(f"Background scraping finished successfully for query: {query}")
        
    except Exception as e:
        # Mark query status as failed if an error occurs
        set_query_status(query, "failed")
        print(f"Error in background task for query '{query}': {e}")

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SmartBuy AI API",
        "message": "Welcome to the Deal Finder API!"
    }

@app.get("/search")
def search(q: str, background_tasks: BackgroundTasks):
    """
    Search endpoint that coordinates caching and background scraping.
    """
    clean_query = q.strip().lower()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Search query parameter 'q' cannot be empty.")
    
    # 1. Check if we've searched this query before and what its status is
    status, last_scraped_at = get_query_status(clean_query)
    
    # CASE 1: Cache is ready and successful -> return products instantly
    if status == "success":
        products = get_cached_products(clean_query)
        return {
            "status": "success",
            "query": q,
            "data": products
        }
        
    # CASE 2: Currently scraping in the background -> tell frontend to wait and check back
    elif status == "scraping":
        return {
            "status": "scraping",
            "query": q,
            "message": "Scrape in progress. Please check back in a few seconds."
        }
        
    # CASE 3: Never scraped before (or previous attempt failed) -> trigger a background scrape
    else:
        # A. Mark status as 'scraping' so multiple requests don't start duplicate scrapers
        set_query_status(clean_query, "scraping")
        
        # B. Add the scrape function to background tasks
        background_tasks.add_task(scrape_and_save_task, clean_query)
        
        # C. Return immediate response
        return {
            "status": "scraping",
            "query": q,
            "message": "Scrape started. Please check back in a few seconds."
        }

@app.get("/search/status")
def search_status(q: str):
    """
    Status polling endpoint.
    Frontend calls this to check if a background scrape task has finished.
    """
    clean_query = q.strip().lower()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Search query parameter 'q' cannot be empty.")
        
    status, last_scraped_at = get_query_status(clean_query)
    
    return {
        "query": q,
        "status": status if status else "not_started",
        "last_scraped_at": last_scraped_at
    }
