"""
Qdrant Stars Dashboard - Streamlit App
A professional dashboard to showcase Qdrant stars' contributions
"""
import streamlit as st
import json
from datetime import datetime
from typing import List, Dict
import utils
from utils import (
    load_stars, save_stars, add_or_update_star, delete_star,
    get_star_by_id, get_star_by_name, get_current_month_contributions,
    validate_url, extract_youtube_id, verify_admin_credentials,
    extract_url_metadata
)

# Page configuration
st.set_page_config(
    page_title="Qdrant Stars Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .star-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border: 1px solid #e8e8e8;
    }
    .star-name {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .star-role {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .contribution-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 3px solid #667eea;
    }
    .contribution-type {
        font-weight: 600;
        color: #667eea;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .contribution-title {
        font-weight: 500;
        color: #333;
        margin-top: 0.5rem;
        font-size: 0.95rem;
    }
    .month-badge {
        background: #667eea;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.95;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .bio-text {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-top: 0.5rem;
    }
    .profile-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    .profile-card-item {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8e8e8;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .profile-card-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .profile-card-name {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .profile-card-role {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    .profile-card-stats {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e8e8e8;
    }
    .profile-stat {
        flex: 1;
        text-align: center;
    }
    .profile-stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #667eea;
    }
    .profile-stat-label {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.25rem;
    }
    .star-tile {
        background: white;
        border-radius: 16px;
        padding: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #e8e8e8;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        overflow: hidden;
        height: 500px;
        display: flex;
        flex-direction: column;
        margin-bottom: 1.5rem;
    }
    .star-tile:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    .star-tile-container {
        position: relative;
        width: 100%;
        margin-bottom: 1.5rem;
        height: 500px;
    }
    .star-tile-wrapper {
        position: relative;
        width: 100%;
        z-index: 1;
    }
    /* Make button overlay the card - target buttons that are siblings of star-tile-container */
    div:has(.star-tile-container) ~ div[data-testid="stButton"],
    div[data-testid="column"]:has(.star-tile-container) ~ div[data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 500px !important;
        z-index: 10 !important;
        margin: 0 !important;
        padding: 0 !important;
        margin-top: -500px !important;
    }
    div:has(.star-tile-container) ~ div[data-testid="stButton"] > button,
    div[data-testid="column"]:has(.star-tile-container) ~ div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 500px !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        box-shadow: none !important;
        min-height: 500px !important;
        color: black !important;
    }
    div:has(.star-tile-container) ~ div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:has(.star-tile-container) ~ div[data-testid="stButton"] > button:hover {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    div:has(.star-tile-container) ~ div[data-testid="stButton"] > button > p {
        color: black !important;
    }
    .star-tile-image {
        width: 100%;
        height: 250px;
        object-fit: cover;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        flex-shrink: 0;
    }
    .star-tile-content {
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
    }
    .star-tile-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    .star-tile-role {
        color: #667eea;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1rem;
        flex-shrink: 0;
    }
    .star-tile-bio {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 1rem;
        flex: 1;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 0;
    }
    .star-tile-stats {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: auto;
        padding-top: 1rem;
        border-top: 1px solid #e8e8e8;
        flex-shrink: 0;
    }
    .star-tile-stat {
        background: #f8f9fa;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        color: #667eea;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

def get_star_image_path(star_name: str):
    """Get the image path for a star based on their name"""
    from pathlib import Path
    
    # Try both folder names (stars-img and stars-image)
    for folder_name in ["stars-img", "stars-image"]:
        # Convert name to filename format (lowercase, replace spaces with hyphens)
        filename = star_name.lower().replace(' ', '-').replace('_', '-')
        image_path = Path(folder_name) / f"{filename}.jpg"
        
        # Check if file exists
        if image_path.exists():
            return str(image_path)
        
        # Try alternative formats
        alt_path = Path(folder_name) / f"{star_name.lower().replace(' ', '_')}.jpg"
        if alt_path.exists():
            return str(alt_path)
    
    # Return None if no image found
    return None

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'editing_star' not in st.session_state:
        st.session_state.editing_star = None
    if 'login_error' not in st.session_state:
        st.session_state.login_error = False
    if 'selected_star_id' not in st.session_state:
        st.session_state.selected_star_id = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'grid'  # 'grid' or 'detail'

def render_youtube_preview(url: str):
    """Render YouTube video preview"""
    video_id = extract_youtube_id(url)
    if video_id:
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <iframe width="100%" height="400" 
                    src="https://www.youtube.com/embed/{video_id}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"[Watch on YouTube]({url})")

def render_profile_card_compact(star: Dict):
    """Render a compact profile card for grid view"""
    name = star.get('name', 'Unknown')
    role = star.get('role', '')
    contributions = star.get('contributions', [])
    
    # Count contributions by type
    youtube_count = len([c for c in contributions if c.get('type', '').lower() == 'youtube'])
    medium_count = len([c for c in contributions if c.get('type', '').lower() == 'medium'])
    linkedin_count = len([c for c in contributions if c.get('type', '').lower() == 'linkedin'])
    substack_count = len([c for c in contributions if c.get('type', '').lower() == 'substack'])
    meetups_count = len([c for c in contributions if c.get('type', '').lower() in ['meetups/events', 'meetups', 'events']])
    opensource_count = len([c for c in contributions if c.get('type', '').lower() in ['open source', 'opensource']])
    other_count = len(contributions) - youtube_count - medium_count - linkedin_count - substack_count - meetups_count - opensource_count
    
    # Use name as identifier (URL-safe)
    import urllib.parse
    star_name_encoded = urllib.parse.quote(name)
    
    # Build stats HTML with all contribution types
    stats_html = ""
    if youtube_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{youtube_count}</div><div class="profile-stat-label">YouTube</div></div>'
    if medium_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{medium_count}</div><div class="profile-stat-label">Medium</div></div>'
    if linkedin_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{linkedin_count}</div><div class="profile-stat-label">LinkedIn</div></div>'
    if substack_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{substack_count}</div><div class="profile-stat-label">Substack</div></div>'
    if meetups_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{meetups_count}</div><div class="profile-stat-label">Meetups</div></div>'
    if opensource_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{opensource_count}</div><div class="profile-stat-label">Open Source</div></div>'
    if other_count > 0:
        stats_html += f'<div class="profile-stat"><div class="profile-stat-number">{other_count}</div><div class="profile-stat-label">Other</div></div>'
    
    st.markdown(f"""
    <div class="profile-card-item" onclick="window.location.href='?star_name={star_name_encoded}'">
        <div class="profile-card-name">{name}</div>
        <div class="profile-card-role">{role}</div>
        <div class="profile-card-stats">
            {stats_html if stats_html else '<div class="profile-stat"><div class="profile-stat-number">0</div><div class="profile-stat-label">No contributions</div></div>'}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_star_detail(star: Dict):
    """Render detailed star profile with categorized contributions"""
    name = star.get('name', 'Unknown')
    role = star.get('role', '')
    bio = star.get('bio', '')
    contributions = star.get('contributions', [])
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_star_id = None
        st.session_state.view_mode = 'grid'
        st.rerun()
    
    st.markdown(f"""
    <div class="star-card">
        <div class="star-name">{name}</div>
        <div class="star-role">{role}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if bio:
        st.markdown(f'<div class="bio-text">{bio}</div>', unsafe_allow_html=True)
    
    if not contributions:
        st.info("No contributions yet.")
        return
    
    # Categorize contributions
    youtube_contribs = [c for c in contributions if c.get('type', '').lower() == 'youtube']
    medium_contribs = [c for c in contributions if c.get('type', '').lower() == 'medium']
    linkedin_contribs = [c for c in contributions if c.get('type', '').lower() == 'linkedin']
    substack_contribs = [c for c in contributions if c.get('type', '').lower() == 'substack']
    meetups_contribs = [c for c in contributions if c.get('type', '').lower() in ['meetups/events', 'meetups', 'events']]
    opensource_contribs = [c for c in contributions if c.get('type', '').lower() in ['open source', 'opensource']]
    other_contribs = [c for c in contributions if c.get('type', '').lower() not in [
        'youtube', 'medium', 'linkedin', 'substack', 'meetups/events', 'meetups', 'events', 'open source', 'opensource'
    ]]
    
    # Create tabs for different contribution types
    tabs = []
    tab_labels = []
    
    if youtube_contribs:
        tabs.append(youtube_contribs)
        tab_labels.append(f"🎥 YouTube ({len(youtube_contribs)})")
    if medium_contribs:
        tabs.append(medium_contribs)
        tab_labels.append(f"📝 Medium ({len(medium_contribs)})")
    if linkedin_contribs:
        tabs.append(linkedin_contribs)
        tab_labels.append(f"💼 LinkedIn ({len(linkedin_contribs)})")
    if substack_contribs:
        tabs.append(substack_contribs)
        tab_labels.append(f"📰 Substack ({len(substack_contribs)})")
    if meetups_contribs:
        tabs.append(meetups_contribs)
        tab_labels.append(f"🎪 Meetups/Events ({len(meetups_contribs)})")
    if opensource_contribs:
        tabs.append(opensource_contribs)
        tab_labels.append(f"💻 Open Source ({len(opensource_contribs)})")
    if other_contribs:
        tabs.append(other_contribs)
        tab_labels.append(f"📄 Other ({len(other_contribs)})")
    
    if tabs:
        st_tabs = st.tabs(tab_labels)
        
        for idx, (contrib_list, tab_label) in enumerate(zip(tabs, tab_labels)):
            with st_tabs[idx]:
                # Group by month
                monthly_contribs = {}
                for contrib in contrib_list:
                    month = contrib.get('month', 'Unknown')
                    if month not in monthly_contribs:
                        monthly_contribs[month] = []
                    monthly_contribs[month].append(contrib)
                
                # Sort months (most recent first)
                sorted_months = sorted(monthly_contribs.keys(), reverse=True)
                
                for month in sorted_months:
                    st.markdown(f'<div class="month-badge">{month}</div>', unsafe_allow_html=True)
                    
                    for contrib in monthly_contribs[month]:
                        contrib_type = contrib.get('type', '')
                        title = contrib.get('title', '')
                        url = contrib.get('url', '').strip()
                        description = contrib.get('description', '').strip()
                        contrib_type_lower = contrib_type.lower().strip()
                        
                        # Types that should not show descriptions
                        no_description_types = ['linkedin', 'substack', 'open source', 'opensource', 'meetups/events', 'meetups', 'events']
                        should_hide_description = contrib_type_lower in no_description_types
                        
                        # For LinkedIn, make title clickable (embedded link, no description)
                        if contrib_type_lower == 'linkedin':
                            st.markdown(f"""
                            <div class="contribution-item">
                                <div class="contribution-type">{contrib_type}</div>
                                <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none;">
                                    <div class="contribution-title">{title}</div>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # For other types, show title and View button
                            # Hide description for Open Source, Substack (like LinkedIn)
                            # Never show description if type is in no_description_types
                            if should_hide_description:
                                # No description for these types
                                st.markdown(f"""
                                <div class="contribution-item">
                                    <div class="contribution-type">{contrib_type}</div>
                                    <div class="contribution-title">{title}</div>
                                    <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 0.9rem; margin-top: 0.5rem; display: inline-block;">View →</a>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # Show description for other types if available
                                show_description = description and description.strip()
                                st.markdown(f"""
                                <div class="contribution-item">
                                    <div class="contribution-type">{contrib_type}</div>
                                    <div class="contribution-title">{title}</div>
                                    {f'<p style="color: #666; font-size: 0.85rem; margin-top: 0.5rem;">{description}</p>' if show_description else ''}
                                    <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 0.9rem; margin-top: 0.5rem; display: inline-block;">View →</a>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show YouTube preview if it's a YouTube video
                            if contrib_type.lower() == 'youtube':
                                render_youtube_preview(url)
                        
                        st.markdown("<br>", unsafe_allow_html=True)

def dashboard_page():
    """Clean dashboard page for stars to view their progress"""
    st.markdown('<div class="main-header">⭐ Qdrant Stars Dashboard</div>', unsafe_allow_html=True)
    
    stars = load_stars()
    
    # Check if a star is selected (from URL parameter or session state)
    query_params = st.query_params
    selected_name = query_params.get("star_name", st.session_state.selected_star_id)
    
    if selected_name:
        import urllib.parse
        selected_name = urllib.parse.unquote(selected_name)
        selected_star = get_star_by_name(stars, selected_name)
        if selected_star:
            st.session_state.selected_star_id = selected_name
            st.session_state.view_mode = 'detail'
            render_star_detail(selected_star)
            return
        else:
            st.session_state.selected_star_id = None
            st.session_state.view_mode = 'grid'
    
    if not stars:
        st.info("✨ No stars added yet. Check back soon!")
        return
    
    # Statistics
    total_contributions = sum(len(star.get('contributions', [])) for star in stars)
    
    # Calculate previous month contributions
    from datetime import datetime, timedelta
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    previous_month_contribs = sum(
        len([
            c for c in star.get('contributions', [])
            if c.get('month', '').startswith(last_month)
        ])
        for star in stars
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(stars)}</div>
            <div class="stat-label">Stars</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_contributions}</div>
            <div class="stat-label">Total Contributions</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{previous_month_contribs}</div>
            <div class="stat-label">Previous Month</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search
    search_term = st.text_input("🔍 Search", "", placeholder="Search by name or role...")
    
    # Filter stars
    filtered_stars = stars
    if search_term:
        filtered_stars = [
            star for star in stars
            if search_term.lower() in star.get('name', '').lower()
            or search_term.lower() in star.get('role', '').lower()
        ]
    
    if not filtered_stars:
        st.info("No stars found matching your search.")
        return
    
    # Display stars in grid with image tiles
    cols = st.columns(3)
    for idx, star in enumerate(filtered_stars):
        with cols[idx % 3]:
            name = star.get('name', 'Unknown')
            role = star.get('role', '')
            bio = star.get('bio', '')
            contributions = star.get('contributions', [])
            
            # Get image path
            image_path = get_star_image_path(name)
            
            # Count contributions by type
            youtube_count = len([c for c in contributions if c.get('type', '').lower() == 'youtube'])
            medium_count = len([c for c in contributions if c.get('type', '').lower() == 'medium'])
            linkedin_count = len([c for c in contributions if c.get('type', '').lower() == 'linkedin'])
            substack_count = len([c for c in contributions if c.get('type', '').lower() == 'substack'])
            meetups_count = len([c for c in contributions if c.get('type', '').lower() in ['meetups/events', 'meetups', 'events']])
            opensource_count = len([c for c in contributions if c.get('type', '').lower() in ['open source', 'opensource']])
            other_count = len(contributions) - youtube_count - medium_count - linkedin_count - substack_count - meetups_count - opensource_count
            
            # Build stats badges
            stats_badges = []
            if youtube_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{youtube_count} YouTube</span>')
            if medium_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{medium_count} Medium</span>')
            if linkedin_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{linkedin_count} LinkedIn</span>')
            if substack_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{substack_count} Substack</span>')
            if meetups_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{meetups_count} Meetups</span>')
            if opensource_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{opensource_count} Open Source</span>')
            if other_count > 0:
                stats_badges.append(f'<span class="star-tile-stat">{other_count} Other</span>')
            
            # Build stats HTML
            stats_html = ''.join(stats_badges) if stats_badges else '<span class="star-tile-stat">No contributions yet</span>'
            
            # Use Streamlit button for clickable cards
            import urllib.parse
            star_name_encoded = urllib.parse.quote(name)
            
            # Button key for unique identification
            button_key = f"star_card_{idx}_{name.replace(' ', '_').replace('/', '_')}"
            
            # Create a container to hold both card and button
            with st.container():
                # Create fully clickable tile with image
                if image_path:
                    # Get image as base64 or use direct path
                    import base64
                    from pathlib import Path
                    
                    # Read image and convert to base64 for embedding
                    try:
                        with open(image_path, "rb") as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                            img_src = f"data:image/jpeg;base64,{img_data}"
                    except:
                        img_src = image_path
                    
                    # Create container with card
                    st.markdown(f"""
                    <div class="star-tile-container">
                        <div class="star-tile-wrapper">
                            <div class="star-tile">
                                <img src="{img_src}" class="star-tile-image" alt="{name}" style="width: 100%; height: 250px; object-fit: cover; display: block;">
                                <div class="star-tile-content">
                                    <div class="star-tile-name">{name}</div>
                                    <div class="star-tile-role">{role}</div>
                                    {f'<div class="star-tile-bio">{bio}</div>' if bio else ''}
                                    <div class="star-tile-stats">
                                        {stats_html}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # No image - show gradient placeholder
                    st.markdown(f"""
                    <div class="star-tile-container">
                        <div class="star-tile-wrapper">
                            <div class="star-tile">
                                <div class="star-tile-image"></div>
                                <div class="star-tile-content">
                                    <div class="star-tile-name">{name}</div>
                                    <div class="star-tile-role">{role}</div>
                                    {f'<div class="star-tile-bio">{bio}</div>' if bio else ''}
                                    <div class="star-tile-stats">
                                        {stats_html}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Button that will trigger navigation - positioned absolutely over the card
                if st.button("View Profile", key=button_key, use_container_width=True, type="secondary"):
                    st.session_state.selected_star_id = name
                    st.session_state.view_mode = 'detail'
                    st.rerun()

def login_page():
    """Admin login page"""
    st.markdown('<div class="main-header">🔐 Admin Login</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if verify_admin_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.login_error = False
                st.success("Login successful!")
                st.rerun()
            else:
                st.session_state.login_error = True
                st.error("Invalid username or password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.login_error:
        st.info("💡 Default credentials: username=`admin`, password=`qdrant2024` (change in utils.py or environment variables)")

def admin_page():
    """Admin page for managing stars - requires authentication"""
    if not st.session_state.authenticated:
        st.warning("🔒 Please login to access the admin dashboard.")
        if st.button("Go to Login"):
            st.session_state.page = "Login"
            st.rerun()
        return
    
    # Logout button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.success("Logged out successfully!")
            st.rerun()
    
    st.markdown('<div class="main-header">🔐 Admin Dashboard</div>', unsafe_allow_html=True)
    
    stars = load_stars()
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["➕ Manage Stars", "📊 Manage Contributions", "🗑️ Delete Stars"])
    
    with tab1:
        st.markdown("### Add or Edit Star")
        
        # Select existing star to edit
        star_names = [star.get('name', 'Unknown') for star in stars]
        
        if star_names:
            selected = st.selectbox(
                "Select star to edit (or create new)",
                ["Create New"] + star_names
            )
            
            editing_star = None
            if selected != "Create New":
                editing_star = get_star_by_name(stars, selected)
        else:
            editing_star = None
        
        # Form fields
        name = st.text_input(
            "Name",
            value=editing_star.get('name', '') if editing_star else ''
        )
        
        role = st.text_input(
            "Role/Title",
            value=editing_star.get('role', '') if editing_star else '',
            help="e.g., Developer Advocate, ML Engineer, etc."
        )
        
        bio = st.text_area(
            "Bio/Description",
            value=editing_star.get('bio', '') if editing_star else '',
            help="Brief description about the star"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Save Star", use_container_width=True):
                if not name:
                    st.error("Name is required!")
                else:
                    star_data = {
                        'name': name,
                        'role': role,
                        'bio': bio,
                        'contributions': editing_star.get('contributions', []) if editing_star else []
                    }
                    add_or_update_star(star_data)
                    st.success(f"Star {'updated' if editing_star else 'added'} successfully!")
                    st.rerun()
        
        if editing_star:
            with col2:
                # Add confirmation for delete
                delete_key = f"delete_confirm_{editing_star.get('name', '').replace(' ', '_')}"
                if delete_key not in st.session_state:
                    st.session_state[delete_key] = False
                
                if not st.session_state[delete_key]:
                    if st.button("🗑️ Delete Star", use_container_width=True, type="secondary"):
                        st.session_state[delete_key] = True
                        st.rerun()
                else:
                    st.warning(f"⚠️ Are you sure you want to delete {editing_star.get('name', 'this star')}?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ Confirm Delete", use_container_width=True, type="primary"):
                            delete_star(editing_star.get('name', ''))
                            st.session_state[delete_key] = False
                            st.success(f"Star '{editing_star.get('name', '')}' deleted successfully!")
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state[delete_key] = False
                            st.rerun()
    
    with tab2:
        st.markdown("### Manage Contributions")
        
        if not stars:
            st.warning("No stars available. Add a star first!")
        else:
            # Select star
            star_options = {s.get('name', 'Unknown'): s.get('name', 'Unknown') for s in stars}
            selected_star_name = st.selectbox("Select Star", list(star_options.keys()))
            selected_star = get_star_by_name(stars, selected_star_name)
            
            if selected_star:
                st.markdown(f"**Managing contributions for: {selected_star.get('name')}**")
                
                # Existing contributions
                contributions = selected_star.get('contributions', [])
                
                if contributions:
                    st.markdown("#### Existing Contributions")
                    for idx, contrib in enumerate(contributions):
                        with st.expander(f"📍 {contrib.get('type')} - {contrib.get('title')} ({contrib.get('month')})"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.json(contrib)
                            with col2:
                                if st.button(f"🗑️ Delete", key=f"del_contrib_{idx}"):
                                    contributions.pop(idx)
                                    selected_star['contributions'] = contributions
                                    add_or_update_star(selected_star)
                                    st.success("Contribution deleted!")
                                    st.rerun()
                
                st.markdown("---")
                st.markdown("#### Add New Contribution")
                
                col1, col2 = st.columns(2)
                with col1:
                    contrib_type = st.selectbox(
                        "Contribution Type",
                        ["YouTube", "Medium", "LinkedIn", "Substack", "Meetups/Events", "Open Source", "Other"]
                    )
                with col2:
                    month = st.text_input(
                        "Month (YYYY-MM)",
                        value=datetime.now().strftime('%Y-%m'),
                        help="Format: YYYY-MM (e.g., 2024-01)"
                    )
                
                url = st.text_input("URL", key="contribution_url", help="Paste URL and click 'Extract Metadata' to auto-fill title and description")
                
                # Initialize session state for extracted data
                if 'extracted_title' not in st.session_state:
                    st.session_state.extracted_title = ''
                if 'extracted_description' not in st.session_state:
                    st.session_state.extracted_description = ''
                
                # Extract metadata button (skip for LinkedIn, Substack, Meetups/Events, Open Source)
                extract_key = "extract_metadata"
                skip_extraction = contrib_type.lower() in ['linkedin', 'substack', 'meetups/events', 'meetups', 'events', 'open source', 'opensource']
                
                if not skip_extraction:
                    if st.button("🔍 Extract Metadata from URL", key=extract_key):
                        if url and url.strip():
                            if validate_url(url, contrib_type.lower()):
                                with st.spinner("Extracting metadata..."):
                                    metadata = extract_url_metadata(url, contrib_type)
                                    if metadata:
                                        st.session_state.extracted_title = metadata.get('title', '')
                                        st.session_state.extracted_description = metadata.get('description', metadata.get('author', ''))
                                        st.success("Metadata extracted successfully! Title and description fields have been updated.")
                                        st.rerun()
                                    else:
                                        st.warning("Could not extract metadata. Please enter manually.")
                            else:
                                st.warning(f"URL may not be valid for {contrib_type}")
                        else:
                            st.error("Please enter a URL first")
                else:
                    if contrib_type.lower() == 'linkedin':
                        st.info("💡 LinkedIn: Just enter a title and paste the link. No metadata extraction needed.")
                    elif contrib_type.lower() == 'substack':
                        st.info("💡 Substack: Just enter a title and paste the link. No metadata extraction needed.")
                    elif contrib_type.lower() in ['meetups/events', 'meetups', 'events']:
                        st.info("💡 Meetups/Events: Enter event name and link. No metadata extraction available.")
                    elif contrib_type.lower() in ['open source', 'opensource']:
                        st.info("💡 Open Source: Enter contribution title and link. No metadata extraction available.")
                
                # Use extracted data if available, otherwise use empty string
                title_value = st.session_state.extracted_title if st.session_state.extracted_title else ''
                desc_value = st.session_state.extracted_description if st.session_state.extracted_description else ''
                
                title = st.text_input(
                    "Title",
                    value=title_value,
                    key="contribution_title",
                    help="Title will be auto-filled if you extract metadata"
                )
                
                description = st.text_area(
                    "Description (optional)",
                    value=desc_value,
                    key="contribution_description",
                    help="Description will be auto-filled if you extract metadata"
                )
                
                if st.button("➕ Add Contribution"):
                    if not title or not url:
                        st.error("Title and URL are required!")
                    elif not validate_url(url, contrib_type.lower()):
                        st.warning(f"URL may not be valid for {contrib_type}")
                    else:
                        new_contrib = {
                            'type': contrib_type,
                            'title': title,
                            'url': url,
                            'month': month,
                            'description': description
                        }
                        contributions.append(new_contrib)
                        selected_star['contributions'] = contributions
                        add_or_update_star(selected_star)
                        # Clear extracted data after adding
                        st.session_state.extracted_title = ''
                        st.session_state.extracted_description = ''
                        st.success("Contribution added successfully!")
                        st.rerun()
    
    with tab3:
        st.markdown("### Delete Stars")
        st.markdown("⚠️ **Warning**: Deleting a star will permanently remove all their contributions.")
        
        if not stars:
            st.warning("No stars available to delete.")
        else:
            # List all stars with delete option
            st.markdown("#### Select a star to delete:")
            
            for star in stars:
                star_name = star.get('name', 'Unknown')
                star_role = star.get('role', '')
                contributions_count = len(star.get('contributions', []))
                
                with st.expander(f"🗑️ {star_name} ({star_role}) - {contributions_count} contributions"):
                    st.markdown(f"**Name**: {star_name}")
                    st.markdown(f"**Role**: {star_role}")
                    st.markdown(f"**Contributions**: {contributions_count}")
                    
                    # Delete confirmation
                    delete_key = f"delete_star_{star_name.replace(' ', '_')}"
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False
                    
                    if not st.session_state[delete_key]:
                        if st.button(f"🗑️ Delete {star_name}", key=f"delete_btn_{star_name.replace(' ', '_')}", type="secondary"):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.error(f"⚠️ Are you sure you want to delete **{star_name}**? This action cannot be undone!")
                        st.warning(f"This will delete {contributions_count} contribution(s) as well.")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button(f"✅ Confirm Delete {star_name}", key=f"confirm_delete_{star_name.replace(' ', '_')}", type="primary"):
                                delete_star(star_name)
                                st.session_state[delete_key] = False
                                st.success(f"✅ Star '{star_name}' deleted successfully!")
                                st.rerun()
                        with col_cancel:
                            if st.button(f"❌ Cancel", key=f"cancel_delete_{star_name.replace(' ', '_')}"):
                                st.session_state[delete_key] = False
                                st.rerun()

def main():
    """Main app function"""
    init_session_state()
    
    # Simple navigation without sidebar for cleaner look
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page = st.radio(
            "Navigation",
            ["⭐ Dashboard", "🔐 Admin"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Route to appropriate page
    if page == "⭐ Dashboard":
        dashboard_page()
    elif page == "🔐 Admin":
        if not st.session_state.authenticated:
            login_page()
        else:
            admin_page()

if __name__ == "__main__":
    main()
