# ⭐ Qdrant Stars Dashboard

A professional Streamlit dashboard to showcase and manage Qdrant stars' contributions including YouTube videos, Medium articles, LinkedIn posts, and monthly activity tracking.

## Features

- 📊 **Clean Dashboard View**: Beautiful, minimal profile cards for stars to view their contributions
- 🔐 **Secure Admin Panel**: Password-protected admin interface for managing stars and contributions
- 🎥 **YouTube Support**: Embedded video previews
- 📝 **Medium Articles**: Link previews and tracking
- 💼 **LinkedIn Posts**: Contribution tracking
- 📅 **Monthly Tracking**: Contributions organized by month
- 🎨 **Professional Design**: Clean, modern UI with custom styling
- 📱 **Responsive Layout**: Works on all screen sizes

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown (usually `http://localhost:8501`)

3. **Dashboard**: Clean interface for stars to view their contributions and progress
4. **Admin Dashboard**: 
   - Navigate to "Admin" page
   - Login with admin credentials (default: username=`admin`, password=`qdrant2024`)
   - Add/Edit stars with their information
   - Manage contributions (YouTube, Medium, LinkedIn, etc.)
   - Delete contributions or stars

## Data Storage

The app uses JSON files for data storage (located in `data/stars.json`). This is simple and works well for links-only storage. If you need more advanced features or want to use Supabase, you can easily extend the `utils.py` file to add database integration.

## Admin Authentication

The admin dashboard is password-protected. Default credentials are:
- **Username**: `admin`
- **Password**: `qdrant2024`

To change credentials:
1. Set environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD`
2. Or modify `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` in `utils.py`

## Adding Stars

1. Go to Admin page and login
2. Click "Manage Stars" tab
3. Fill in:
   - **Star ID**: Unique identifier (e.g., username)
   - **Name**: Full name
   - **Role**: Title/position
   - **Bio**: Brief description
4. Click "Save Star"

## Adding Contributions

1. Go to Admin page and login
2. Click "Manage Contributions" tab
3. Select a star
4. Fill in:
   - **Type**: YouTube, Medium, LinkedIn, or Other
   - **Title**: Contribution title
   - **URL**: Link to the content
   - **Month**: Format YYYY-MM (e.g., 2024-01)
   - **Description**: Optional description
5. Click "Add Contribution"

## Preview Features

- YouTube videos: Embedded previews on the dashboard
- Medium articles: Link previews
- LinkedIn posts: Link previews

## File Structure

```
stars-dashboard/
├── app.py              # Main Streamlit application
├── utils.py            # Utility functions and data management
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # Data storage directory
    └── stars.json     # Stars and contributions data (auto-created)
```

## Customization

The app uses custom CSS for styling. You can modify the styles in `app.py` to match your branding. The color scheme uses a purple gradient (#667eea to #764ba2) that can be easily changed.

## Future Enhancements

- Supabase integration for cloud storage
- Image uploads for star profiles
- Analytics and statistics
- Export functionality
- Search and filtering improvements

## License

This project is open source and available for use.

