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
    get_star_by_id, get_current_month_contributions,
    validate_url, extract_youtube_id, verify_admin_credentials
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
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'editing_star' not in st.session_state:
        st.session_state.editing_star = None
    if 'login_error' not in st.session_state:
        st.session_state.login_error = False

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

def render_star_card(star: Dict):
    """Render a clean star's profile card"""
    name = star.get('name', 'Unknown')
    role = star.get('role', '')
    bio = star.get('bio', '')
    contributions = star.get('contributions', [])
    
    st.markdown(f"""
    <div class="star-card">
        <div class="star-name">{name}</div>
        <div class="star-role">{role}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if bio:
        st.markdown(f'<div class="bio-text">{bio}</div>', unsafe_allow_html=True)
    
    if contributions:
        st.markdown("### Contributions")
        
        # Group contributions by month
        monthly_contribs = {}
        for contrib in contributions:
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
                url = contrib.get('url', '')
                description = contrib.get('description', '')
                
                st.markdown(f"""
                <div class="contribution-item">
                    <div class="contribution-type">{contrib_type}</div>
                    <div class="contribution-title">{title}</div>
                    <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">View →</a>
                </div>
                """, unsafe_allow_html=True)
                
                # Show YouTube preview if it's a YouTube video
                if contrib_type.lower() == 'youtube':
                    render_youtube_preview(url)
    
    st.markdown("---")

def dashboard_page():
    """Clean dashboard page for stars to view their progress"""
    st.markdown('<div class="main-header">⭐ Qdrant Stars Dashboard</div>', unsafe_allow_html=True)
    
    stars = load_stars()
    
    if not stars:
        st.info("✨ No stars added yet. Check back soon!")
        return
    
    # Statistics
    total_contributions = sum(len(star.get('contributions', [])) for star in stars)
    current_month_contribs = sum(
        len(get_current_month_contributions(star.get('contributions', [])))
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
            <div class="stat-label">Contributions</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{current_month_contribs}</div>
            <div class="stat-label">This Month</div>
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
    
    # Display stars
    for star in filtered_stars:
        render_star_card(star)

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
    tab1, tab2 = st.tabs(["➕ Manage Stars", "📊 Manage Contributions"])
    
    with tab1:
        st.markdown("### Add or Edit Star")
        
        # Select existing star to edit
        star_names = [f"{star.get('name')} ({star.get('id')})" for star in stars]
        
        if star_names:
            selected = st.selectbox(
                "Select star to edit (or create new)",
                ["Create New"] + star_names
            )
            
            editing_star = None
            if selected != "Create New":
                selected_id = selected.split('(')[1].split(')')[0]
                editing_star = get_star_by_id(stars, selected_id)
        else:
            editing_star = None
        
        # Form fields
        col1, col2 = st.columns(2)
        with col1:
            star_id = st.text_input(
                "Star ID (unique identifier)",
                value=editing_star.get('id', '') if editing_star else '',
                help="Unique ID for this star (e.g., username, email)"
            )
        with col2:
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
                if not star_id or not name:
                    st.error("Star ID and Name are required!")
                else:
                    star_data = {
                        'id': star_id,
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
                if st.button("🗑️ Delete Star", use_container_width=True):
                    delete_star(star_id)
                    st.success(f"Star deleted successfully!")
                    st.rerun()
    
    with tab2:
        st.markdown("### Manage Contributions")
        
        if not stars:
            st.warning("No stars available. Add a star first!")
        else:
            # Select star
            star_options = {f"{s.get('name')} ({s.get('id')})": s.get('id') for s in stars}
            selected_star_name = st.selectbox("Select Star", list(star_options.keys()))
            selected_star_id = star_options[selected_star_name]
            selected_star = get_star_by_id(stars, selected_star_id)
            
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
                        ["YouTube", "Medium", "LinkedIn", "Other"]
                    )
                with col2:
                    month = st.text_input(
                        "Month (YYYY-MM)",
                        value=datetime.now().strftime('%Y-%m'),
                        help="Format: YYYY-MM (e.g., 2024-01)"
                    )
                
                title = st.text_input("Title")
                
                url = st.text_input("URL")
                
                description = st.text_area("Description (optional)")
                
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
                        st.success("Contribution added successfully!")
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
