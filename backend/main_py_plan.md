# 📋 Backend Server Plan: `backend/main.py`

This document details the design, structure, endpoints, data flow, and dependencies required to implement the FastAPI backend entry point (`main.py`) for the **SmartBuy AI** product deal finder application.

---

## 🔍 Overview & Role of `main.py`

`backend/main.py` serves as the entry point for our FastAPI application. It is responsible for:
1. **Request Routing:** Handling requests from the frontend client.
2. **CORS Configuration:** Allowing our frontend web page to safely request data from the backend.
3. **Caching Logic Orchestration:** 
   - Checking the database first to see if results for a given query exist and are fresh.
   - Deciding whether to serve cached results or initiate a fresh scrape.
4. **Background Task Scheduling:** Triggering scraper execution in a background thread to prevent request timeouts and keep the user experience responsive.
5. **Data Enrichment & AI Ranking (Optional/Phase 4):** Cooperating with Gemini AI to rank and explain why certain deals are recommended.

---

## 🔌 API Endpoints Specification

Here are the endpoints we plan to implement in `main.py`:

### 1. Root Endpoint (Health Check)
* **URL:** `GET /`
* **Purpose:** Verification that the server is alive and running. Used for deployment health checks (e.g., Render.com).
* **Response:**
  ```json
  {
    "status": "healthy",
    "service": "SmartBuy AI API",
    "timestamp": "2026-06-22T20:53:00Z"
  }
  ```

### 2. Search & Aggregation Endpoint
* **URL:** `GET /search`
* **Query Parameters:**
  * `q` (string, required): The search query (e.g., `laptop`, `iphone 13`).
  * `budget` (integer/float, optional): Maximum budget filter.
  * `refresh` (boolean, default `false`): If `true`, bypasses cache and forces a fresh scrape.
* **Flow Chart of Operations:**
  ```mermaid
  graph TD
      A[Frontend GET /search] --> B{Check DB Cache}
      B -- Cache Found & Fresh (< 3 days) --> C[Rank / Filter Products]
      C --> D[Return JSON Response with Data]
      B -- Cache Empty or Expired --> E[Add Scraper to BackgroundTasks]
      E --> F[Create/Update Query Log to 'scraping' State]
      F --> G[Return JSON: Status 'scraping']
      G -.-> H[Background: Run Scrapers]
      H --> I[Background: Save results to DB]
      I --> J[Background: Update Query Log to 'success']
  ```
* **Response Types:**
  
  #### Case A: Scraping Started (Cache Miss)
  * **HTTP Status:** `202 Accepted`
  * **Response:**
    ```json
    {
      "status": "scraping",
      "query": "laptop",
      "message": "Scrape in progress. Please check back in a few seconds."
    }
    ```

  #### Case B: Data Found (Cache Hit)
  * **HTTP Status:** `200 OK`
  * **Response:**
    ```json
    {
      "status": "success",
      "query": "laptop",
      "total_results": 5,
      "data": [
        {
          "name": "HP Laptop 15-FD0532NIA Intel Core i3 13th Gen",
          "price": 115680.0,
          "rating": 4.5,
          "buys": 12,
          "link": "https://priceoye.pk/laptops/hp/...",
          "website": "priceoye"
        }
      ]
    }
    ```

### 3. Server-Side Scraper Status Endpoint (Polling helper)
* **URL:** `GET /search/status`
* **Query Parameters:**
  * `q` (string, required): The search query.
* **Purpose:** Allows the frontend to check if a background scrape has finished.
* **Response:**
  ```json
  {
    "query": "laptop",
    "status": "success", // or "scraping", "failed"
    "last_updated": "2026-06-22T20:53:00Z"
  }
  ```

---

## 🛠️ Internal Server Logic

### A. Dependencies and Packages
```python
from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import datetime
# From our other backend packages:
# from backend.database import get_cached_products, save_products, get_query_status, update_query_status
# from backend.priceoye_scraper import scrape_priceoye
# from backend.daraz_scraper import scrape_daraz
# from backend.amazon_scraper import scrape_amazon
```

### B. Background Tasks Workflow
Because scraping multiple sites (PriceOye, Daraz, Amazon) can take anywhere from **3 to 15 seconds**, running it synchronously inside the request/response lifecycle would cause the frontend client to time out. 
FastAPI's built-in `BackgroundTasks` executes functions after returning the HTTP response:

```python
def scrape_and_save_task(query: str):
    try:
        # 1. Update status in database to 'scraping'
        update_query_status(query, "scraping")
        
        # 2. Run scrapers
        scraped_data = []
        
        # Initial implementation: PriceOye
        priceoye_results = scrape_priceoye(query)
        scraped_data.extend(priceoye_results)
        
        # Optional/Future: Daraz & Amazon scrapers
        # daraz_results = scrape_daraz(query)
        # scraped_data.extend(daraz_results)
        
        # 3. Save aggregated products to database
        save_products(query, scraped_data)
        
        # 4. Mark search query status as 'success'
        update_query_status(query, "success")
    except Exception as e:
        update_query_status(query, "failed", error_message=str(e))
```

### C. CORS Configuration
To allow local browser files or frontend hosts to connect to `http://localhost:8000`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all. In production, restrict to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📂 Database Integration Model
To make caching work, we need a table/log of queries to keep track of statuses:
1. **`queries` Table:**
   * `query` (text, primary key)
   * `status` (text: `'scraping'`, `'success'`, `'failed'`)
   * `last_scraped_at` (timestamp)
2. **`products` Table:**
   * `id` (serial primary key)
   * `query` (text, foreign key)
   * `name` (text)
   * `price` (float)
   * `rating` (float)
   * `buys` (integer)
   * `link` (text)
   * `website` (text)
   * `scraped_at` (timestamp)

---

## 🚀 Plan Steps & Milestones

1. **Step 1: Environment Readiness**
   - Place dependency list in `requirements.txt`.
   - Setup `.env` configuration file loader (`python-dotenv`).

2. **Step 2: Database Layer (`backend/database.py`)**
   - Create functions to check cache and write scraped items.
   - Use SQLite (`market_data.db`) or Supabase based on configuration.

3. **Step 3: Refactoring Scrapers to Modular Functions**
   - Convert `priceoye_scraper.py` into a reusable module function: `def scrape_priceoye(search_term: str) -> List[dict]`.

4. **Step 4: Implementing `backend/main.py` Router & Tasks**
   - Set up FastAPI app.
   - Configure CORS.
   - Write endpoints `/`, `/search`, and `/search/status`.
   - Connect background tasks to run the modular scrapers.

5. **Step 5: Testing and Integration**
   - Run server using `uvicorn backend.main:app --reload`.
   - Test endpoints with `curl` or FastAPI Docs (`/docs`).
