document.getElementById("searchForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    // Get user_id from localStorage
    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
        alert("Please log in first");
        window.location.href = "/"; // Redirect to login page
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
        console.log("Sending search data:", searchData);
        
        const response = await fetch("/save-search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(searchData),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Failed to save search");
        }

        alert("Search saved successfully!");
        
        // Optional: Clear form
        document.getElementById("searchForm").reset();
        
    } catch (error) {
        console.error("Error saving search:", error);
        alert(`Error: ${error.message}`);
    }
});

// Add this to verify user_id is properly stored
document.addEventListener("DOMContentLoaded", () => {
    const user_id = localStorage.getItem("user_id");
    console.log("Current user_id:", user_id);
});