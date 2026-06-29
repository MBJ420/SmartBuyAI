const BACKEND_URL = "http://localhost:8000";
let pollingInterval;

async function startSearch() {
    const searchInput = document.getElementById("searchInput").value;
    const budgetInput = document.getElementById("budgetInput").value;
    const ratingInput = document.getElementById("ratingInput").value;
    
    const resultsGrid = document.getElementById("resultsGrid");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const loadingText = document.getElementById("loadingText");
    const errorAlert = document.getElementById("errorAlert");
    const aiActionContainer = document.getElementById("aiActionContainer");

    // Clear previous results and errors
    resultsGrid.innerHTML = "";
    errorAlert.classList.add("d-none");
    aiActionContainer.classList.add("d-none"); // Hide AI button

    // Show loading UI
    loadingSpinner.style.display = "block";
    loadingText.innerText = "Initiating search...";

    // If there is an active polling loop, stop it
    if (pollingInterval) clearInterval(pollingInterval);

    // Construct URL with filters
    let url = `${BACKEND_URL}/search?q=${encodeURIComponent(searchInput)}`;
    if (budgetInput) url += `&budget=${encodeURIComponent(budgetInput)}`;
    if (ratingInput) url += `&min_rating=${encodeURIComponent(ratingInput)}`;

    try {
        // Step 1: Send initial request to the backend
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Step 2: Handle the response based on status
        if (data.status === "success") {
            // Data is instantly ready (from cache)
            renderProducts(data.data, false); // false = not AI
        } else if (data.status === "scraping") {
            // Data is being scraped in the background. We need to poll for updates.
            loadingText.innerText = data.message;
            pollForResults(searchInput, budgetInput, ratingInput);
        } else {
            throw new Error(`Unknown status: ${data.status}`);
        }

    } catch (error) {
        showError(`Failed to connect to the backend. Make sure the Python server is running on port 8000. Error: ${error.message}`);
    }
}

function pollForResults(query, budget, rating) {
    const loadingText = document.getElementById("loadingText");
    let dots = 0;

    // Check status every 3 seconds
    pollingInterval = setInterval(async () => {
        try {
            // Update loading text animation
            dots = (dots + 1) % 4;
            loadingText.innerText = "Scraping data from PriceOye" + ".".repeat(dots);

            // Fetch current status
            const response = await fetch(`${BACKEND_URL}/search/status?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.status === "success") {
                // Scraping is done! Stop polling and fetch the actual data
                clearInterval(pollingInterval);
                loadingText.innerText = "Data ready! Loading...";
                fetchFinalData(query, budget, rating);
            } else if (data.status === "failed") {
                // Scraping failed
                clearInterval(pollingInterval);
                showError("The background scraping task failed. Please try a different search term.");
            }
            // If status is still "scraping", we do nothing and wait for the next interval

        } catch (error) {
            clearInterval(pollingInterval);
            showError(`Error checking status: ${error.message}`);
        }
    }, 3000); // 3000 milliseconds = 3 seconds
}

async function fetchFinalData(query, budget, rating) {
    try {
        let url = `${BACKEND_URL}/search?q=${encodeURIComponent(query)}`;
        if (budget) url += `&budget=${encodeURIComponent(budget)}`;
        if (rating) url += `&min_rating=${encodeURIComponent(rating)}`;
        
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === "success") {
            renderProducts(data.data, false);
        } else {
            showError("Data was marked as success, but failed to load.");
        }
    } catch (error) {
        showError(`Error fetching final data: ${error.message}`);
    }
}

async function getAIRecommendations() {
    const searchInput = document.getElementById("searchInput").value;
    const budgetInput = document.getElementById("budgetInput").value;
    const ratingInput = document.getElementById("ratingInput").value;
    const resultsGrid = document.getElementById("resultsGrid");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const loadingText = document.getElementById("loadingText");
    const errorAlert = document.getElementById("errorAlert");
    const aiActionContainer = document.getElementById("aiActionContainer");

    resultsGrid.innerHTML = "";
    errorAlert.classList.add("d-none");
    aiActionContainer.classList.add("d-none"); 

    loadingSpinner.style.display = "block";
    loadingText.innerText = "✨ Asking Gemini AI to pick the best products...";

    let url = `${BACKEND_URL}/ai-recommend?q=${encodeURIComponent(searchInput)}`;
    if (budgetInput) url += `&budget=${encodeURIComponent(budgetInput)}`;
    if (ratingInput) url += `&min_rating=${encodeURIComponent(ratingInput)}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        if (data.status === "success") {
            // Check for AI API error response
            if (data.data && data.data.length > 0 && data.data[0].error) {
                showError(data.data[0].error);
            } else {
                renderProducts(data.data, true); // true = yes, this is AI
            }
        } else {
            throw new Error(`Failed to get AI recommendations: ${data.status}`);
        }
    } catch (error) {
        showError(`Error contacting AI: ${error.message}`);
    }
}

function renderProducts(products, isAI = false) {
    const loadingSpinner = document.getElementById("loadingSpinner");
    const resultsGrid = document.getElementById("resultsGrid");
    const aiActionContainer = document.getElementById("aiActionContainer");

    // Hide loading
    loadingSpinner.style.display = "none";

    if (!products || products.length === 0) {
        resultsGrid.innerHTML = `
            <div class="col-12 text-center mt-4">
                <h4 class="text-muted">No products found. Try adjusting your filters!</h4>
            </div>
        `;
        return;
    }

    // Show AI button only if it's a normal search and products were found
    if (!isAI) {
        aiActionContainer.classList.remove("d-none");
    }

    // Loop through the data and generate HTML for each product card
    let html = "";
    for (const product of products) {
        // Format the price with commas (e.g., 50000 -> 50,000)
        const formattedPrice = product.price ? product.price.toLocaleString() : "N/A";

        // Handle missing images safely
        const imageUrl = product.image_url || "https://via.placeholder.com/200?text=No+Image";

        // AI specific UI (gradient border, explanation text)
        const cardClass = isAI ? "border border-success border-2 shadow-lg" : "shadow-sm";
        const aiBadge = isAI ? `<span class="badge bg-success mb-2">✨ AI Top Pick</span>` : "";
        const aiExplanation = isAI && product.ai_explanation 
            ? `<div class="mt-2 p-2 bg-light border-start border-success border-4 text-dark small rounded">
                 <strong>AI says:</strong> ${product.ai_explanation}
               </div>` 
            : "";

        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card product-card h-100 ${cardClass}">
                    <div class="product-img-wrapper">
                        <img src="${imageUrl}" class="product-img" alt="${product.name}">
                    </div>
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                ${aiBadge}
                                <span class="badge bg-secondary mb-2">${product.website}</span>
                            </div>
                            ${product.rating ? `<span class="badge bg-warning text-dark"><i class="fas fa-star"></i> ${product.rating}</span>` : ''}
                        </div>
                        <h5 class="card-title fw-bold text-truncate" title="${product.name}">${product.name}</h5>
                        <p class="product-price mt-auto mb-2">Rs. ${formattedPrice}</p>
                        ${aiExplanation}
                        <a href="${product.link}" target="_blank" class="btn btn-outline-primary w-100 mt-3">
                            View Deal <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    // Inject the HTML into the page
    resultsGrid.innerHTML = html;
}

function showError(message) {
    const loadingSpinner = document.getElementById("loadingSpinner");
    const errorAlert = document.getElementById("errorAlert");

    loadingSpinner.style.display = "none";
    errorAlert.classList.remove("d-none");
    errorAlert.innerText = message;
}
