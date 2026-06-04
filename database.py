from pymongo import MongoClient, TEXT
from config import MONGO_URI

# ── Connect ───────────────────────────────────────────────────────────────────
client = MongoClient(MONGO_URI)
db = client["cinemacityhub"]
files_col = db["files"]
users_col = db["users"]

# ── Indexes ───────────────────────────────────────────────────────────────────
files_col.create_index([("file_name_lower", TEXT)])
files_col.create_index([("language", 1)])
files_col.create_index([("quality", 1)])
users_col.create_index([("user_id", 1)], unique=True)


# ── File Operations ───────────────────────────────────────────────────────────

def save_file(file_id, file_name, file_unique_id, language="unknown", quality="unknown"):
    """Save a new file to DB. Returns True if saved, False if duplicate."""
    if files_col.find_one({"file_unique_id": file_unique_id}):
        return False
    files_col.insert_one({
        "file_id": file_id,
        "file_name": file_name,
        "file_name_lower": file_name.lower(),
        "file_unique_id": file_unique_id,
        "language": language.lower(),
        "quality": quality.lower(),
    })
    return True


def search_files(movie_name: str, language: str = None):
    """Search files by movie name and optional language."""
    query = {"file_name_lower": {"$regex": movie_name.lower(), "$options": "i"}}
    if language and language.lower() != "all":
        query["language"] = {"$regex": language.lower(), "$options": "i"}
    return list(files_col.find(query).limit(15))


def get_languages(movie_name: str):
    """Get all available languages for a movie name."""
    results = files_col.find(
        {"file_name_lower": {"$regex": movie_name.lower(), "$options": "i"}}
    )
    langs = set(r.get("language", "unknown") for r in results)
    return sorted(langs)


def get_total_files():
    """Return total indexed file count."""
    return files_col.count_documents({})


def delete_file(file_unique_id: str):
    """Delete a file by unique ID."""
    files_col.delete_one({"file_unique_id": file_unique_id})


# ── User Operations ───────────────────────────────────────────────────────────

def save_user(user_id: int, first_name: str, username: str = None):
    """Save or update a user."""
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
        }},
        upsert=True
    )


def get_total_users():
    """Return total registered user count."""
    return users_col.count_documents({})


def get_all_users():
    """Return all user IDs for broadcast."""
    return [u["user_id"] for u in users_col.find({}, {"user_id": 1})]
