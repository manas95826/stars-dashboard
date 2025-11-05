"""
Utility functions for the Qdrant Stars Dashboard
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Data directory
DATA_DIR = Path("data")
STARS_FILE = DATA_DIR / "stars.json"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(exist_ok=True)

def load_stars() -> List[Dict]:
    """Load stars data from JSON file"""
    ensure_data_dir()
    if not STARS_FILE.exists():
        return []
    
    try:
        with open(STARS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_stars(stars: List[Dict]):
    """Save stars data to JSON file"""
    ensure_data_dir()
    with open(STARS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stars, f, indent=2, ensure_ascii=False)

def get_star_by_id(stars: List[Dict], star_id: str) -> Optional[Dict]:
    """Get a star by their ID"""
    for star in stars:
        if star.get('id') == star_id:
            return star
    return None

def add_or_update_star(star_data: Dict):
    """Add a new star or update existing one"""
    stars = load_stars()
    
    # Check if star exists
    existing_idx = None
    for idx, star in enumerate(stars):
        if star.get('id') == star_data.get('id'):
            existing_idx = idx
            break
    
    if existing_idx is not None:
        stars[existing_idx] = star_data
    else:
        stars.append(star_data)
    
    save_stars(stars)

def delete_star(star_id: str):
    """Delete a star by ID"""
    stars = load_stars()
    stars = [star for star in stars if star.get('id') != star_id]
    save_stars(stars)

def get_current_month_contributions(contributions: List[Dict]) -> List[Dict]:
    """Get contributions for the current month"""
    current_month = datetime.now().strftime('%Y-%m')
    return [
        contrib for contrib in contributions
        if contrib.get('month', '').startswith(current_month)
    ]

def validate_url(url: str, url_type: str) -> bool:
    """Basic URL validation"""
    if not url or not url.strip():
        return False
    
    url = url.strip()
    
    if url_type == 'youtube':
        return 'youtube.com' in url or 'youtu.be' in url
    elif url_type == 'medium':
        return 'medium.com' in url or 'towardsdatascience.com' in url
    elif url_type == 'linkedin':
        return 'linkedin.com' in url
    
    return url.startswith('http://') or url.startswith('https://')

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return None

# Admin credentials (default - should be changed in production)
# In production, use environment variables or Streamlit secrets
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "qdrant2025"

def get_admin_credentials():
    """Get admin credentials from environment or defaults"""
    username = os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
    password = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    return username, password

def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin credentials"""
    admin_username, admin_password = get_admin_credentials()
    return username == admin_username and password == admin_password

