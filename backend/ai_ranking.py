import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with the key from the environment
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def rank_products(products, budget, min_rating=None):
    """
    Takes a list of products and asks Gemini to pick the top 3 best recommendations.
    Returns a list of dictionaries with the product info and an AI explanation.
    """
    if not api_key:
        return [{"error": "GEMINI_API_KEY not found in .env file."}]

    if not products:
        return []

    # Prepare a simplified list of products to send to the AI
    # We only send necessary fields to save tokens
    product_summaries = []
    for p in products:
        summary = {
            "name": p.get("name"),
            "price": p.get("price"),
            "rating": p.get("rating"),
            "link": p.get("link"),
            "website": p.get("website"),
            "image_url": p.get("image_url")
        }
        product_summaries.append(summary)

    prompt = f"""
    You are an expert shopping assistant. I have a list of products that match a user's search.
    The user's maximum budget is Rs. {budget if budget else 'Unlimited'}.
    The user's minimum acceptable rating is {min_rating if min_rating else 'Any'} stars.
    
    Here is the list of products:
    {json.dumps(product_summaries, indent=2)}

    Please select the top 3 best products from this list based on value for money, specifications (if inferable from name), and rating.
    Return ONLY a JSON array of 3 objects. Do not include markdown formatting like ```json or anything else. Just the raw JSON.
    Each object must have exactly these keys:
    "name": (the product name)
    "price": (the price as a number)
    "rating": (the rating)
    "link": (the product link)
    "website": (the website name)
    "image_url": (the image URL)
    "ai_explanation": (A 1-2 sentence explanation of why you recommend this specific product over the others)
    """

    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Call the model
        response = model.generate_content(prompt)
        
        # Clean the response text to ensure it's valid JSON (sometimes AI adds markdown code blocks)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        ranked_products = json.loads(response_text)
        return ranked_products
        
    except Exception as e:
        print(f"AI Ranking Error: {e}")
        return [{"error": f"Failed to get AI recommendations: {str(e)}"}]
