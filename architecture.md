# 🏗️ SmartBuy AI: System Architecture & Data Flow

This document outlines the files, components, data flows, and execution lifecycle of the **SmartBuy AI** deal finder application. 

For our initial setup, we will use **PriceOye** (utilizing `requests` and `BeautifulSoup` for lightweight scraping) to keep testing fast and stable.

---

## 📂 1. Directory & File Structure

Here is where every file sits in the project workspace:

```text
SmartBuyAI/
│
├── backend/                       # 🐍 Python FastAPI Backend
│   ├── __init__.py                # Makes backend a Python package
│   ├── main.py                    # FastAPI server entry point and search endpoint
│   ├── database.py                # Supabase database initialization and helper functions
│   └── priceoye_scraper.py        # PriceOye scraping function (requests + bs4)
│
├── frontend/                      # 🎨 Static Frontend Client
│   ├── index.html                 # HTML search input, styling, and JavaScript logic
│   └── style.css                  # Simple modern styling adjustments
│
├── .env                           # 🔑 API keys and secrets (never commit to git)
├── .gitignore                     # Ignores venv, .env, and caches
└── requirements.txt               # List of Python dependencies
```

---

## ⚙️ 2. File Roles & Descriptions

Here is what each file does and what libraries it utilizes:

### A. Backend Files
1. **`requirements.txt`**
   * **Role:** Lists the external libraries we need to install.
   * **Libraries:** `fastapi`, `uvicorn`, `supabase`, `requests`, `beautifulsoup4`, `python-dotenv`.
2. **`backend/priceoye_scraper.py`**
   * **Role:** Contains a single function: `scrape_priceoye(search_term: str) -> list[dict]`.
   * **Action:** It constructs a search query to PriceOye, fetches the page using `requests`, parses cards using `BeautifulSoup`, and returns clean data.
3. **`backend/database.py`**
   * **Role:** Connects to Supabase using credentials in `.env`.
   * **Functions:**
     * `get_cached_products(search_term)`: Queries Supabase.
     * `cache_products(products_list)`: Saves scraped results to Supabase.
4. **`backend/main.py`**
   * **Role:** Starts the server and listens for network calls.
   * **Endpoint:** `GET /search?q={search_term}`.
   * **Execution:** orchestrates checking the cache, running the scraper via FastAPI's `BackgroundTasks` if empty, and returning data.

### B. Frontend Files
1. **`frontend/index.html`**
   * **Role:** The user interface. Contains an input box, search button, and empty results container.
   * **JavaScript logic:** Triggered when the button is clicked. It calls `fetch("http://localhost:8000/search?q=...")` and injects HTML cards using template literals.

---

## 🔄 3. Execution Lifecycle: What Happens When?

Here is the exact sequence of events when a user uses the app:

### Step 1: User Actions (Frontend)
* The user opens `frontend/index.html` in their web browser.
* They type `"dell laptop"` in the search bar and click **Find Best Deals**.
* JavaScript intercepts the button click, clears the results grid, and shows a loading spinner.

### Step 2: The Network Request (Frontend to Backend)
* JavaScript fires an HTTP request:
  `GET http://localhost:8000/search?q=dell+laptop`
* The request travels over the local network (or internet when deployed) to the running FastAPI server.

### Step 3: Database Cache Check (Backend)
* FastAPI intercepts the request inside `backend/main.py`.
* It calls `get_cached_products("dell laptop")` from `backend/database.py`.
* **Database queries take less than 100ms.**

#### 🟢 Scenario A: Data is already in the database
1. If the database returns matching products, FastAPI immediately returns them.
2. The response returns with a `{"status": "success", "data": [...]}` status.

#### 🟡 Scenario B: Data is NOT in the database
1. If the database is empty, FastAPI registers a **Background Task** to run the scraper:
   `background_tasks.add_task(scrape_and_save, "dell laptop")`
2. FastAPI immediately returns a response to the user:
   `{"status": "scraping", "message": "Scrape in progress. Try again in 5 seconds."}`
3. The server then begins executing `scrape_priceoye("dell laptop")` in a separate background thread.
4. Once scraping is complete, `backend/database.py` saves the results to Supabase.

### Step 4: Displaying the Results (Frontend)
* The JavaScript receives the response from FastAPI.
* **If `"status" === "scraping"`:** JavaScript displays the "Scraping in progress" message and schedules a retry (`setTimeout`) in 5 seconds.
* **If `"status" === "success"`:** JavaScript loops through the array of products, formats them into Bootstrap card templates, and injects them into the grid using `.innerHTML`.
