# 🚀 Detailed Master Guide: Smart Product Deal Finder SaaS

Welcome to the detailed step-by-step guide for building your Free SaaS app! This guide is designed to take you from a complete beginner in connecting backends and frontends to successfully deploying a full-stack AI-powered application.

---

## 🛠️ Tech Stack & Recommendations

Based on your current experience (knowing HTML/Python) and your goal of learning the complete app flow:

### 1. Frontend: Vanilla HTML/CSS/JS with Bootstrap (or Tailwind)
**Recommendation:** Keep it simple! You don't need a heavy framework like React yet. 
- **Structure:** Standard `.html` files.
- **Styling:** Use **Bootstrap 5** (via CDN). It allows you to create beautiful, responsive UI components (like the PriceOye card you already have) without writing much CSS. 
- **Logic:** Vanilla JavaScript (`fetch` API) to send user inputs to your Python backend and receive the ranked results.

### 2. Backend: Python + FastAPI
FastAPI is incredibly fast, modern, and very easy to learn. It also automatically generates documentation for your API, which is great for beginners.
- You will use FastAPI to create "endpoints" (URLs that your frontend can talk to).
- You will use **Pandas** here to filter and sort the scraped data.

### 3. Web Scraping: BeautifulSoup + Playwright
- **PriceOye:** Mostly static or simple dynamic content, easily scraped with `requests` and `BeautifulSoup`. (I saw your `priceoye_product_card.html` — this is exactly the kind of HTML structure we will scrape!).
- **Amazon:** Since Amazon has heavy anti-bot measures, you will eventually use **Playwright** (which simulates a real browser) combined with rotating proxies to bypass their security.

### 4. Database: Supabase
- Used to cache scraped data so you don't have to scrape Amazon/PriceOye every single time a user searches.

### 5. AI / LLM: Google Gemini
- Used to take the final filtered Pandas DataFrame and rank the laptops/products.

---

## 🗺️ Step-by-Step Implementation Plan

### Phase 1: Environment & Project Setup
Before writing code, we need a clean workspace.

1. **Create Virtual Environment:** 
   Open your terminal in VSCode and run:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```
2. **Install Dependencies:**
   ```bash
   pip install fastapi uvicorn pandas beautifulsoup4 requests google-generativeai supabase
   ```
3. **Directory Structure:** Create these folders in your project:
   - `/backend` (Put all your Python files here)
   - `/frontend` (Put your HTML/CSS/JS here)
   - `.env` (To store your Gemini and Supabase API keys securely)

### Phase 2: Building the FastAPI Backend
This is where the brain of your app lives.

1. **Create `main.py` in `/backend`:**
   This file will start your server.
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI()

   # This allows your frontend to talk to your backend
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"], # In production, change this to your frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   @app.get("/")
   def read_root():
       return {"message": "Welcome to the Deal Finder API!"}
   ```
2. **Run the server:**
   ```bash
   uvicorn backend.main:app --reload
   ```
   *You can now visit `http://localhost:8000/docs` to see your API!*

### Phase 3: Writing the Scrapers
1. **PriceOye Scraper (`scraper_priceoye.py`):**
   - Write a function that takes a `search_term` (e.g., "laptop").
   - Use `requests.get()` to fetch the PriceOye search page.
   - Use `BeautifulSoup` to find the `<a class="product-card">` tags (just like the HTML file you showed me) and extract the Product Name, Price, and Image URL.
   - Return this data as a list of Python dictionaries.
2. **Amazon Scraper (Later):**
   - Keep this for later, as it will require Playwright to bypass captchas.
3. **Pandas Integration:**
   - Convert the list of dictionaries into a Pandas DataFrame.
   - Filter out items that don't match the user's budget.

### Phase 4: Connecting the LLM (Gemini)
1. **Create `ai_ranking.py`:**
   - Write a function that takes your filtered Pandas DataFrame (converted to a JSON string or CSV format).
   - Send a prompt to Gemini: *"Here is a list of laptops with prices. The user has a budget of X and wants something reliable. Rank the top 3 best value options and explain why in short JSON format."*
   - Parse the JSON response from Gemini.

### Phase 5: The Frontend & "Connecting" the Two
This is the part you were unsure about. How does the frontend talk to the backend? 

**The Magic of the `fetch` API:**
1. Create `index.html` in your `/frontend` folder.
2. Add a simple form (Input for Product Name, Input for Budget, Submit Button).
3. Add a `<script>` tag at the bottom.
4. When the button is clicked, JavaScript will send a request to your Python server:

```javascript
// Inside your frontend/index.html script
async function searchProducts() {
    const product = document.getElementById("productInput").value;
    const budget = document.getElementById("budgetInput").value;

    // Call your Python FastAPI backend
    const response = await fetch(`http://localhost:8000/search?product=${product}&budget=${budget}`);
    
    // Get the ranked data back from Python
    const data = await response.json();

    // Loop through the data and create HTML product cards dynamically!
    console.log(data); 
}
```

### Phase 6: User Tracking & Supabase Integration
1. **Simple Tracking:** In FastAPI, you can access the user's IP address from the request object (`request.client.host`). You can save this IP in Supabase with a daily count. If they exceed 5 searches, return an error message.
2. **Database Caching:** Before calling your scraper scripts, check Supabase: *“Do I already have data for ‘Dell Laptops’ scraped in the last 3 days?”* If yes, use it. If no, run the scraper and save the new data to Supabase.

### Phase 7: Deployment (The Final Boss)
1. **Frontend:** Drag and drop your `/frontend` folder into **Netlify** or **Vercel**. It will give you a live URL instantly (e.g., `my-deal-finder.netlify.app`).
2. **Backend:** Push your code to GitHub and connect it to **Render.com**. Render will host your FastAPI Python server for free (e.g., `my-python-api.onrender.com`).
3. **CORS Update:** Go back to your Python code and update `allow_origins=["https://my-deal-finder.netlify.app"]` so only your frontend is allowed to talk to your backend (Security 101!).

---

## 🚦 Next Steps
Read through this plan. The best way to learn is to build it one phase at a time.
**When you are ready, let's start with Phase 1 and Phase 2: Getting the FastAPI server running.** Just let me know!
