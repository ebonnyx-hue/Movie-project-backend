from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import httpx
import os
from dotenv import load_dotenv
import json
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="Movie Recommendation API",
             description="API for movie recommendations using TMDB",
             version="1.0.0")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory database
users_db: Dict[str, Dict] = {}

# User Models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Auth Router
auth_router = APIRouter(prefix="/api/auth")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@auth_router.post("/register")
async def register_user(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    users_db[user.username] = user_dict
    return {"message": "User registered successfully"}

@auth_router.post("/login")
async def login(user_data: UserLogin):
    user = users_db.get(user_data.username)
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user_data.username
    }

# Mount routers
app.include_router(auth_router)

# TMDB API Key (temporary for testing)
TMDB_API_KEY = "a0ab31064a79c0d939a22d24b2361210"

# Genre mapping
GENRE_MAPPING = {
    "action": 28,
    "adventure": 12,
    "comedy": 35,
    "drama": 18,
    "horror": 27,
    "romance": 10749,
    "sci-fi": 878,
    "thriller": 53
}

# Fallback movies in case of API failure
FALLBACK_MOVIES = [
    {
        "id": 1,
        "title": "The Shawshank Redemption",
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "vote_average": 8.7,
        "release_date": "1994-09-23"
    },
    {
        "id": 2,
        "title": "The Godfather",
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "vote_average": 8.7,
        "release_date": "1972-03-14"
    },
    {
        "id": 3,
        "title": "The Dark Knight",
        "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "vote_average": 8.5,
        "release_date": "2008-07-16"
    }
]

# AI Router
ai_router = APIRouter(prefix="/api/ai")

@ai_router.get("/genre/{genre_id}")
async def get_genre_content(genre_id: int):
    try:
        print(f"Fetching content for genre ID: {genre_id}")
        
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Fetch movies by genre
            movies_url = "https://api.themoviedb.org/3/discover/movie"
            movies_params = {
                "api_key": TMDB_API_KEY,
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
            
            # Fetch TV shows by genre
            tv_url = "https://api.themoviedb.org/3/discover/tv"
            tv_params = {
                "api_key": TMDB_API_KEY,
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
            
            # Make parallel requests
            movies_response, tv_response = await asyncio.gather(
                client.get(movies_url, params=movies_params),
                client.get(tv_url, params=tv_params)
            )
            
            result = {
                "movies": [],
                "tv_shows": []
            }
            
            if movies_response.status_code == 200:
                movies_data = movies_response.json()
                result["movies"] = [
                    {
                        "id": movie["id"],
                        "title": movie["title"],
                        "overview": movie["overview"],
                        "poster_path": movie["poster_path"],
                        "vote_average": movie["vote_average"],
                        "release_date": movie.get("release_date", "")
                    }
                    for movie in movies_data.get("results", [])[:10]  # Get top 10 movies
                ]
            
            if tv_response.status_code == 200:
                tv_data = tv_response.json()
                result["tv_shows"] = [
                    {
                        "id": show["id"],
                        "name": show["name"],
                        "overview": show["overview"],
                        "poster_path": show["poster_path"],
                        "vote_average": show["vote_average"],
                        "first_air_date": show.get("first_air_date", "")
                    }
                    for show in tv_data.get("results", [])[:10]  # Get top 10 TV shows
                ]
            
            return result
            
    except Exception as e:
        print(f"Error in get_genre_content: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_router.post("/recommend")
async def get_recommendations(prompt: dict):
    try:
        print("Received recommendation request with prompt:", prompt)
        prompt_lower = prompt['prompt'].lower()
        print("Processing prompt:", prompt_lower)
        
        # Find matching genre
        genre_id = None
        for genre_name, genre_id_value in GENRE_MAPPING.items():
            if genre_name in prompt_lower:
                genre_id = genre_id_value
                print(f"Found matching genre: {genre_name} (ID: {genre_id})")
                break
        
        # Create TMDB API client with timeout
        async with httpx.AsyncClient(timeout=2.0) as client:
            # If genre found, search by genre
            if genre_id:
                print(f"Found genre ID: {genre_id}, searching TMDB")
                url = f"https://api.themoviedb.org/3/discover/movie"
                params = {
                    "api_key": TMDB_API_KEY,
                    "with_genres": genre_id,
                    "sort_by": "popularity.desc",
                    "page": 1
                }
            # Otherwise, search by keyword
            else:
                print(f"No genre found, searching TMDB with keyword: {prompt_lower}")
                url = f"https://api.themoviedb.org/3/search/movie"
                params = {
                    "api_key": TMDB_API_KEY,
                    "query": prompt_lower,
                    "page": 1
                }
            
            print(f"Making request to {url} with params: {params}")
            # Make API request
            response = await client.get(url, params=params)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Raw TMDB response: {json.dumps(data, indent=2)}")
                movies = data.get("results", [])[:5]  # Get top 5 movies
                print(f"Found {len(movies)} movies from TMDB")
                
                # If no movies found, get popular movies
                if not movies:
                    print("No movies found, fetching popular movies")
                    popular_url = f"https://api.themoviedb.org/3/movie/popular"
                    popular_response = await client.get(
                        popular_url,
                        params={"api_key": TMDB_API_KEY, "page": 1}
                    )
                    if popular_response.status_code == 200:
                        popular_data = popular_response.json()
                        print(f"Popular movies response: {json.dumps(popular_data, indent=2)}")
                        movies = popular_data.get("results", [])[:5]
                        print(f"Found {len(movies)} popular movies")
                
                # Format response
                result = {
                    "movies": [
                        {
                            "id": movie["id"],
                            "title": movie["title"],
                            "overview": movie["overview"],
                            "poster_path": movie["poster_path"],
                            "vote_average": movie["vote_average"],
                            "release_date": movie.get("release_date", "")
                        }
                        for movie in movies
                    ]
                }
                print(f"Returning {len(result['movies'])} movies: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"TMDB API error: {response.status_code}")
                print(f"Response content: {response.text}")
                # Return fallback movies on error
                print("Returning fallback movies")
                return {"movies": FALLBACK_MOVIES}
                
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount routers
app.include_router(ai_router) 