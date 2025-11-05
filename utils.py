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

def generate_id_from_name(name: str) -> str:
    """Generate a unique ID from name (slug-like)"""
    import re
    # Convert to lowercase, replace spaces with underscores, remove special chars
    id_str = re.sub(r'[^a-z0-9_]+', '', name.lower().replace(' ', '_'))
    return id_str

def get_star_by_id(stars: List[Dict], identifier: str) -> Optional[Dict]:
    """Get a star by ID or name (backward compatible)"""
    for star in stars:
        # Try by ID first (for backward compatibility)
        if star.get('id') == identifier:
            return star
        # Try by name
        if star.get('name', '').lower() == identifier.lower():
            return star
    return None

def get_star_by_name(stars: List[Dict], name: str) -> Optional[Dict]:
    """Get a star by name"""
    for star in stars:
        if star.get('name', '').lower() == name.lower():
            return star
    return None

def add_or_update_star(star_data: Dict):
    """Add a new star or update existing one"""
    stars = load_stars()
    
    # Generate ID from name if not provided
    if 'id' not in star_data or not star_data.get('id'):
        star_data['id'] = generate_id_from_name(star_data.get('name', ''))
    
    # Check if star exists by name (primary identifier)
    existing_idx = None
    star_name = star_data.get('name', '').lower()
    
    for idx, star in enumerate(stars):
        if star.get('name', '').lower() == star_name:
            existing_idx = idx
            break
    
    if existing_idx is not None:
        # Update existing star, preserve contributions if not provided
        if 'contributions' not in star_data:
            star_data['contributions'] = stars[existing_idx].get('contributions', [])
        stars[existing_idx] = star_data
    else:
        # Add new star
        if 'contributions' not in star_data:
            star_data['contributions'] = []
        stars.append(star_data)
    
    save_stars(stars)

def delete_star(identifier: str):
    """Delete a star by ID or name"""
    stars = load_stars()
    stars = [
        star for star in stars 
        if star.get('id') != identifier and star.get('name', '').lower() != identifier.lower()
    ]
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
    elif url_type == 'substack':
        return 'substack.com' in url
    elif url_type in ['meetups/events', 'meetups', 'events']:
        return True  # Any URL is valid for meetups/events
    elif url_type in ['open source', 'opensource']:
        return True  # Any URL is valid for open source (GitHub, GitLab, etc.)
    
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

def extract_youtube_metadata(url: str) -> Dict:
    """Extract metadata from YouTube URL"""
    try:
        import requests
        video_id = extract_youtube_id(url)
        if not video_id:
            return {}
        
        # Use YouTube oEmbed API
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', ''),
                'author': data.get('author_name', ''),
                'thumbnail': data.get('thumbnail_url', '')
            }
    except Exception:
        pass
    return {}

def extract_medium_metadata(url: str) -> Dict:
    """Extract metadata from Medium article URL"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find title
            title = ''
            if soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            # Try to find description
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title,
                'description': description
            }
    except Exception:
        pass
    return {}

def extract_linkedin_metadata(url: str) -> Dict:
    """Extract metadata from LinkedIn post URL"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find title
            title = ''
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            # Try to find description
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title,
                'description': description
            }
    except Exception:
        pass
    return {}

def extract_substack_metadata(url: str) -> Dict:
    """Extract metadata from Substack article URL"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find title
            title = ''
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            # Try to find description
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title,
                'description': description
            }
    except Exception:
        pass
    return {}

def extract_url_metadata(url: str, url_type: str) -> Dict:
    """Extract metadata from URL based on type"""
    if url_type.lower() == 'youtube':
        return extract_youtube_metadata(url)
    elif url_type.lower() == 'medium':
        return extract_medium_metadata(url)
    elif url_type.lower() == 'substack':
        return extract_substack_metadata(url)
    elif url_type.lower() == 'linkedin':
        # LinkedIn doesn't extract metadata - just use the link
        return {}
    
    # Generic extraction for other URLs
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = ''
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title,
                'description': description
            }
    except Exception:
        pass
    return {}

