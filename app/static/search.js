document.getElementById("searchForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
        alert("Please log in first");
        window.location.href = "/";
        return;
    }

    // Get form data
    const location = document.getElementById("location").value;
    const minPrice = document.getElementById("minPrice").value;
    const maxPrice = document.getElementById("maxPrice").value;
    const petCategory = document.getElementById("petCategory").value;
    const petSize = document.getElementById("petSize").value;

    const searchData = {
        user_id,
        location,
        minPrice: minPrice || null,
        maxPrice: maxPrice || null,
        petCategory: petCategory || null,
        petSize: petSize || null,
    };

    try {
        // Save search history
        await saveSearch(searchData);
        
        // Search for hotels
        const hotels = await searchHotels(searchData);
        
        // Display results
        displayHotels(hotels);
        
    } catch (error) {
        console.error("Error:", error);
        alert(`Error: ${error.message}`);
    }
});

async function saveSearch(searchData) {
    const response = await fetch("/save-search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(searchData),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save search");
    }

    return response.json();
}

async function searchHotels(searchData) {
    const response = await fetch("/search-hotels", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(searchData),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to search hotels");
    }

    return response.json();
}

function displayHotels(result) {
    const resultsContainer = document.getElementById("hotelResults");
    resultsContainer.innerHTML = ""; // Clear previous results

    if (!result.hotels || result.hotels.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <h3>No hotels found matching your criteria</h3>
            </div>
        `;
        return;
    }

    // Add results title
    const titleDiv = document.createElement("div");
    titleDiv.className = "results-title";
    titleDiv.innerHTML = `<h3>${result.message}</h3>`;
    resultsContainer.appendChild(titleDiv);

    // Create hotel cards
    const hotelsGrid = document.createElement("div");
    hotelsGrid.className = "hotels-grid";

    result.hotels.forEach(hotel => {
        const hotelCard = document.createElement("div");
        hotelCard.className = "hotel-card";
        hotelCard.innerHTML = `
            <h3>${hotel.name}</h3>
            <div class="hotel-location">📍 ${hotel.location}</div>
            <div class="hotel-price">💰 Rp ${hotel.price_per_night.toLocaleString('id-ID')} / malam</div>
            <div class="hotel-rating">⭐ ${hotel.rating} / 5.0</div>
            <div class="hotel-pets">
                <div>🐾 Accepts: ${hotel.pet_categories.join(', ')}</div>
                <div>📏 Sizes: ${hotel.pet_sizes.join(', ')}</div>
            </div>
            <div class="hotel-description">${hotel.description}</div>
            <div class="hotel-amenities">
                <strong>Amenities:</strong>
                <ul>
                    ${hotel.amenities.map(amenity => `<li>${amenity}</li>`).join('')}
                </ul>
            </div>
        `;
        hotelsGrid.appendChild(hotelCard);
    });

    resultsContainer.appendChild(hotelsGrid);
}

// Add this to verify user_id is properly stored
document.addEventListener("DOMContentLoaded", () => {
    const user_id = localStorage.getItem("user_id");
    console.log("Current user_id:", user_id);
});