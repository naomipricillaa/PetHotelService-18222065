# PawMates - Pet Hotel Recommendation System 🐶

**Name**: Naomi Pricilla Agustine  
**Student ID**: 18222065

---

## Description
PawMates is a web-based application designed to help pet owners to find the perfect pet-friendly hotels for their furry friends. The system provides personalized hotel recommendations based on user preferences and search history, making it easier for pet owners to find accommodations that suit both their needs and their pets' requirements.

---

## Features
1. **User Authentication**
   - Google OAuth integration for secure login to access the platform
   - Personalized user experience with session management

2. **Hotel Search**
   - Location-based search
   - Price range filtering
   - Pet category filtering (dogs, cats, etc.)
   - Pet size accommodation filtering
   - Real-time search results

3. **Personalized Recommendations**
   - AI-powered recommendation system based on search history
   - Scoring system for hotel matches
   - Customized suggestions based on previous searches
   - Match percentage display for transparency

4. **Customer Service and Support**
   - 24/7 AI-powered chatbot assistance
   - Automated response system for common queries
   - FAQ integration with chatbot responses
   - Seamless handoff to human support when needed

---

## Access Links
- Production: [https://pethotelservice.up.railway.app](https://pethotelservice.up.railway.app)
- Alternative: [https://pet-hotel-service-18222065.vercel.app](https://pet-hotel-service-18222065.vercel.app)
- Documentation: [https://pethotelservice.up.railway.app/docs](https://pethotelservice.up.railway.app/docs)

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- FastAPI framework

### Database
- Supabase

### Additional Technologies
- Google OAuth2 for authentication

---

## Deployment
The application is deployed using **Railway** using Docker containers and **Vercel** for alternative

---

## Local Development Setup

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Then fill in the required environment variables:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- CALLBACK_URL
- SUPABASE_URL
- SUPABASE_KEY

4. Run the development server:
```bash
uvicorn main:app --reload
```

5. Access the application at `http://localhost:8000`

---

## API Documentation

### Authentication

#### `GET /auth/login`
Initiates Google OAuth login. No parameters required.
**Response**:
- **200**: Redirects user to Google authentication page.

#### `POST /auth/logout`
Logs the user out of the system.
**Response**:
- **200**: Returns `{ "message": "Logged out successfully" }`.

#### `GET /auth/callback`
Handles the OAuth callback and exchanges the authorization code for user tokens.
**Parameters**:
- `code` (query, required): Authorization code from Google.
**Response**:
- **200**: Redirects to the home page with the user's ID.
- **422**: Validation error if the code is missing or invalid.

### Search

#### `POST /search-hotels`
Search for hotels based on criteria such as location, price range, pet category, and size.
**Request Body**:
```json
{
  "location": "string",
  "minPrice": "number",
  "maxPrice": "number",
  "petCategory": "string",
  "petSize": "string"
}
```
**Response**:
- **200**: Returns a list of hotels matching the criteria.
- **422**: Validation error if parameters are invalid.

#### `POST /save-search`
Saves the user's search criteria to the database.
**Request Body**:
```json
{
  "user_id": "string",
  "location": "string",
  "minPrice": "number",
  "maxPrice": "number",
  "petCategory": "string",
  "petSize": "string"
}
```
**Response**:
- **200**: Returns `{ "message": "Search data saved successfully" }`.
- **422**: Validation error if parameters are invalid.

### Recommendations

#### `GET /api/generate-api-key/{client_name}`
Generates a new API key for the specified client.
**Parameters**:
- `client_name` (path, required): Name of the client.
**Response**:
- **200**: Returns `{ "client_name": "string", "api_key": "string" }`.

#### `GET /api/recommendations/{user_id}`
Fetches personalized hotel recommendations based on the user's search history.
**Parameters**:
- `user_id` (path, required): User ID.
**Response**:
- **200**: Returns a list of recommended hotels.
- **422**: Validation error if user ID is missing or invalid.

### Default Pages

#### `GET /`
Landing page for the application.
**Response**:
- **200**: Returns the HTML content of the landing page.

#### `GET /login`
Login page for the application.
**Response**:
- **200**: Returns the HTML content of the login page.

#### `GET /home`
Home page for the user after logging in.
**Response**:
- **200**: Returns the HTML content of the home page.

#### `GET /search`
Search page for finding pet-friendly hotels.
**Response**:
- **200**: Returns the HTML content of the search page.

#### `GET /recommendations`
Page for displaying personalized recommendations.
**Response**:
- **200**: Returns the HTML content of the recommendations page.

---
