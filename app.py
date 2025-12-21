"""
Job Hunter Dashboard - Streamlit UI for the job search aggregator.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage import (
    init_db, get_jobs, get_job_by_id, get_stats, 
    update_job_status, get_unscored_jobs
)
from config import GOOGLE_SEARCH_CONFIG, MIN_MATCH_SCORE

# Load API key from Streamlit secrets (if available) and set as environment variable
# This allows the scorer.py to access it via os.environ
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

# Page config
st.set_page_config(
    page_title="Job Hunter 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Dark theme adjustments */
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #0f3460;
    }
    
    .job-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #e94560;
        margin-bottom: 1rem;
    }
    
    .high-match {
        border-left-color: #00d26a !important;
    }
    
    .score-high { color: #00d26a; font-weight: bold; }
    .score-medium { color: #ffc107; font-weight: bold; }
    .score-low { color: #e94560; font-weight: bold; }
    
    .status-new { background: #3498db; }
    .status-reviewed { background: #9b59b6; }
    .status-applied { background: #2ecc71; }
    .status-interviewing { background: #f39c12; }
    .status-rejected { background: #e74c3c; }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def get_score_class(score):
    """Return CSS class based on score."""
    if score is None:
        return ""
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    return "score-low"


def format_score(score):
    """Format score with color."""
    if score is None:
        return "—"
    css_class = get_score_class(score)
    return f'<span class="{css_class}">{score:.0f}</span>'


def run_command(cmd):
    """Run a CLI command and capture output."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return result.stdout + result.stderr, result.returncode == 0
    except Exception as e:
        return str(e), False


# Initialize database if needed
init_db()

# Sidebar navigation
st.sidebar.title("🎯 Job Hunter")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📋 Jobs", "🔍 Job Details", "🔧 Search Config", "⚙️ Actions"],
    index=0
)

st.sidebar.markdown("---")

# Quick stats in sidebar
stats = get_stats()
st.sidebar.metric("Total Jobs", stats['total_jobs'])
if stats['average_match_score']:
    st.sidebar.metric("Avg Match Score", f"{stats['average_match_score']:.0f}/100")


# ============== DASHBOARD PAGE ==============
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.markdown("Overview of your job search progress")
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Jobs", stats['total_jobs'])
    
    with col2:
        high_match = len([j for j in get_jobs(min_score=MIN_MATCH_SCORE, limit=1000)])
        st.metric("⭐ High Match (70+)", high_match)
    
    with col3:
        applied = stats['by_status'].get('applied', 0) + stats['by_status'].get('interviewing', 0)
        st.metric("📤 Applied/Interviewing", applied)
    
    with col4:
        unscored = len(get_unscored_jobs())
        st.metric("⏳ Unscored", unscored)
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Jobs by Company")
        if stats['by_company']:
            df_company = pd.DataFrame(
                list(stats['by_company'].items())[:10], 
                columns=['Company', 'Count']
            )
            fig = px.bar(
                df_company, 
                x='Count', 
                y='Company', 
                orientation='h',
                color='Count',
                color_continuous_scale=['#e94560', '#0f3460']
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No jobs yet. Run a scrape to get started!")
    
    with col2:
        st.subheader("Jobs by Status")
        if stats['by_status']:
            df_status = pd.DataFrame(
                list(stats['by_status'].items()), 
                columns=['Status', 'Count']
            )
            colors = {
                'new': '#3498db',
                'reviewed': '#9b59b6',
                'applied': '#2ecc71',
                'interviewing': '#f39c12',
                'rejected': '#e74c3c'
            }
            fig = px.pie(
                df_status, 
                values='Count', 
                names='Status',
                color='Status',
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status data yet.")
    
    # Score distribution
    st.subheader("Match Score Distribution")
    jobs = get_jobs(limit=500)
    scored_jobs = [j for j in jobs if j.match_score is not None]
    
    if scored_jobs:
        scores = [j.match_score for j in scored_jobs]
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#e94560',
            opacity=0.8
        ))
        fig.add_vline(x=MIN_MATCH_SCORE, line_dash="dash", line_color="#00d26a", 
                      annotation_text=f"Min Target ({MIN_MATCH_SCORE})")
        fig.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Match Score",
            yaxis_title="Number of Jobs"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No scored jobs yet. Run scoring to see the distribution.")


# ============== JOBS LIST PAGE ==============
elif page == "📋 Jobs":
    st.title("📋 Jobs List")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        companies = list(stats['by_company'].keys()) if stats['by_company'] else []
        company_filter = st.selectbox("Company", ["All"] + companies)
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "new", "reviewed", "applied", "interviewing", "rejected"])
    
    with col3:
        min_score = st.slider("Min Score", 0, 100, 0)
    
    with col4:
        sort_by = st.selectbox("Sort by", ["Score (High→Low)", "Score (Low→High)", "Company", "Recent"])
    
    # Get filtered jobs
    jobs = get_jobs(
        company=company_filter if company_filter != "All" else None,
        status=status_filter if status_filter != "All" else None,
        min_score=min_score if min_score > 0 else None,
        limit=200
    )
    
    # Sort
    if sort_by == "Score (Low→High)":
        jobs = sorted(jobs, key=lambda x: x.match_score or 0)
    elif sort_by == "Company":
        jobs = sorted(jobs, key=lambda x: x.company)
    elif sort_by == "Recent":
        jobs = sorted(jobs, key=lambda x: x.scraped_at or "", reverse=True)
    
    st.markdown(f"**Showing {len(jobs)} jobs**")
    st.markdown("---")
    
    # Display jobs
    if not jobs:
        st.info("No jobs match your filters. Try adjusting the criteria or run a scrape.")
    else:
        for job in jobs:
            is_high_match = job.match_score and job.match_score >= MIN_MATCH_SCORE
            card_class = "job-card high-match" if is_high_match else "job-card"
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    title_prefix = "⭐ " if is_high_match else ""
                    st.markdown(f"### {title_prefix}{job.title}")
                    st.markdown(f"**{job.company}** • {job.location or 'Location not specified'}")
                
                with col2:
                    if job.match_score:
                        score_color = "#00d26a" if job.match_score >= 70 else "#ffc107" if job.match_score >= 50 else "#e94560"
                        st.markdown(f"<h2 style='color: {score_color}; margin: 0;'>{job.match_score:.0f}</h2>", unsafe_allow_html=True)
                        st.caption("Match Score")
                    else:
                        st.markdown("**—**")
                        st.caption("Not scored")
                
                with col3:
                    status_colors = {
                        'new': '🔵', 'reviewed': '🟣', 'applied': '🟢', 
                        'interviewing': '🟡', 'rejected': '🔴'
                    }
                    st.markdown(f"{status_colors.get(job.status, '⚪')} **{job.status.upper()}**")
                    if st.button("View Details", key=f"view_{job.id}"):
                        st.session_state['selected_job_id'] = job.id
                        st.rerun()
                
                st.markdown("---")


# ============== JOB DETAILS PAGE ==============
elif page == "🔍 Job Details":
    st.title("🔍 Job Details")
    
    # Job selector
    jobs = get_jobs(limit=500)
    job_options = {f"{j.id}: {j.title[:50]} @ {j.company}": j.id for j in jobs}
    
    selected_job_id = st.session_state.get('selected_job_id')
    
    if job_options:
        # Find default index
        default_idx = 0
        if selected_job_id:
            for i, (label, jid) in enumerate(job_options.items()):
                if jid == selected_job_id:
                    default_idx = i
                    break
        
        selected = st.selectbox(
            "Select a job",
            options=list(job_options.keys()),
            index=default_idx
        )
        job_id = job_options[selected]
        job = get_job_by_id(job_id)
        
        if job:
            # Header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"## {job.title}")
                st.markdown(f"**{job.company}** • {job.location or 'Location not specified'}")
                st.markdown(f"🔗 [View Original Posting]({job.url})")
            
            with col2:
                if job.match_score:
                    score_color = "#00d26a" if job.match_score >= 70 else "#ffc107" if job.match_score >= 50 else "#e94560"
                    st.markdown(f"<h1 style='color: {score_color}; text-align: center;'>{job.match_score:.0f}</h1>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center;'>Match Score</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Status and actions
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Status")
                new_status = st.selectbox(
                    "Update status",
                    ["new", "reviewed", "applied", "interviewing", "rejected"],
                    index=["new", "reviewed", "applied", "interviewing", "rejected"].index(job.status)
                )
                notes = st.text_area("Notes", value=job.notes or "")
                
                if st.button("💾 Save Changes", type="primary"):
                    update_job_status(job.id, new_status, notes)
                    st.success("Status updated!")
                    st.rerun()
            
            with col2:
                st.subheader("Match Analysis")
                if job.match_reasoning:
                    st.markdown(job.match_reasoning)
                else:
                    st.info("This job hasn't been scored yet. Run scoring from the Actions page.")
            
            st.markdown("---")
            
            # Description
            st.subheader("📄 Job Description")
            if job.description:
                with st.expander("View Full Description", expanded=True):
                    st.markdown(job.description[:5000])
            else:
                st.info("No description available.")
            
            # Metadata
            with st.expander("📋 Metadata"):
                st.markdown(f"**Job ID:** {job.id}")
                st.markdown(f"**Scraped:** {job.scraped_at}")
                st.markdown(f"**URL:** {job.url}")
    else:
        st.info("No jobs in the database. Run a scrape to get started!")


# ============== SEARCH CONFIG PAGE ==============
elif page == "🔧 Search Config":
    st.title("🔧 Google Search Configuration")
    st.markdown("Configure parameters for internet-wide job search via Google")
    
    st.info("💡 These settings control how the scraper searches for jobs across the internet using Google Search via ScraperAPI")
    
    # Display current configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 Keywords")
        st.markdown("**Current keywords:**")
        for keyword in GOOGLE_SEARCH_CONFIG['keywords']:
            st.markdown(f"- `{keyword}`")
        
        st.markdown("---")
        
        st.subheader("🎯 Experience Levels")
        st.markdown("**Current levels:**")
        for level in GOOGLE_SEARCH_CONFIG.get('experience_levels', []):
            st.markdown(f"- `{level}`")
        
        st.markdown("---")
        
        st.subheader("📅 Date Range")
        date_range_display = {
            'past_24h': 'Past 24 hours',
            'past_week': 'Past week',
            'past_month': 'Past month',
            'any_time': 'Any time'
        }
        current_date_range = GOOGLE_SEARCH_CONFIG.get('date_range', 'past_week')
        st.markdown(f"**Current:** `{date_range_display.get(current_date_range, current_date_range)}`")
    
    with col2:
        st.subheader("🌐 Target Sites")
        st.markdown("**Included job boards:**")
        for site in GOOGLE_SEARCH_CONFIG.get('included_sites', []):
            st.markdown(f"- `{site}`")
        
        st.markdown("---")
        
        st.subheader("📍 Locations")
        st.markdown(f"**Primary location:** `{GOOGLE_SEARCH_CONFIG.get('primary_location', 'Not set')}`")
        st.markdown(f"**Total target locations:** `{len(GOOGLE_SEARCH_CONFIG.get('locations', []))}`")
        
        with st.expander("View All Locations"):
            for loc in GOOGLE_SEARCH_CONFIG.get('locations', []):
                st.markdown(f"- {loc}")
        
        st.markdown("---")
        
        st.subheader("💰 Salary Range")
        min_sal = GOOGLE_SEARCH_CONFIG.get('min_salary')
        max_sal = GOOGLE_SEARCH_CONFIG.get('max_salary')
        st.markdown(f"**Min:** `${min_sal:,}` | **Max:** `{'No limit' if not max_sal else f'${max_sal:,}'}`")
        
        st.markdown("---")
        
        st.subheader("📊 Results Limit")
        st.markdown(f"**Max results per search:** `{GOOGLE_SEARCH_CONFIG.get('results_per_search', 100)}`")
    
    st.markdown("---")
    
    st.subheader("✏️ Modify Configuration")
    st.markdown("""
    To modify these settings, edit `config.py` and update the `GOOGLE_SEARCH_CONFIG` dictionary.
    
    **Example:**
    ```python
    GOOGLE_SEARCH_CONFIG = {
        "keywords": ["enterprise architect", "CTO", "director technology"],
        "date_range": "past_week",
        "min_salary": 150000,
        # ... other settings
    }
    ```
    
    After editing, restart the Streamlit app for changes to take effect.
    """)
    
    # API Key status
    st.markdown("---")
    st.subheader("🔐 API Key Status")
    
    scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
    if scraperapi_key and scraperapi_key != 'your_key_here':
        st.success("✅ SCRAPERAPI_KEY is configured")
    else:
        st.error("❌ SCRAPERAPI_KEY not found or invalid")
        st.markdown("""
        **To set up ScraperAPI:**
        1. Sign up at [scraperapi.com](https://www.scraperapi.com/)
        2. Get your API key from the dashboard
        3. Add to your shell profile (`~/.zshrc`):
           ```bash
           export SCRAPERAPI_KEY="your_key_here"
           ```
        4. Restart your terminal and Streamlit app
        """)


# ============== ACTIONS PAGE ==============
elif page == "⚙️ Actions":
    st.title("⚙️ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Scrape Jobs")
        st.markdown("Search for jobs across the internet using Google Search via ScraperAPI.")
        
        # Show search configuration summary
        with st.expander("Search Configuration"):
            st.markdown(f"**Keywords:** {len(GOOGLE_SEARCH_CONFIG['keywords'])} configured")
            st.markdown(f"**Target locations:** {GOOGLE_SEARCH_CONFIG.get('primary_location', 'Not set')}")
            st.markdown(f"**Date range:** {GOOGLE_SEARCH_CONFIG.get('date_range', 'past_week')}")
            st.markdown(f"**Job boards:** {len(GOOGLE_SEARCH_CONFIG.get('included_sites', []))} sites")
            st.markdown(f"**Salary min:** ${GOOGLE_SEARCH_CONFIG.get('min_salary', 0):,}")
            st.markdown("\n*View full config in 🔧 Search Config page*")
        
        # Check API key
        scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        if not scraperapi_key or scraperapi_key == 'your_key_here':
            st.error("❌ SCRAPERAPI_KEY not configured. See 🔧 Search Config page.")
            scrape_disabled = True
        else:
            st.success("✅ ScraperAPI key configured")
            scrape_disabled = False
        
        if st.button("🚀 Start Scraping", type="primary", key="scrape", disabled=scrape_disabled):
            with st.spinner("Scraping job sites... This may take a few minutes."):
                # Use the virtual environment's Python
                venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
                output, success = run_command(f"{venv_python} main.py scrape")
                
                if success:
                    st.success("Scraping complete!")
                else:
                    st.warning("Scraping finished with some errors.")
                
                with st.expander("View Output"):
                    st.code(output)
                
                st.rerun()
    
    with col2:
        st.subheader("🎯 Score Jobs")
        st.markdown("Score unscored jobs against your resume using AI.")
        
        unscored = get_unscored_jobs()
        st.info(f"**{len(unscored)}** jobs waiting to be scored")
        
        # Check for API key (supports .env, environment variable, or Streamlit secrets)
        api_key_set = (
            os.environ.get('ANTHROPIC_API_KEY') or 
            "ANTHROPIC_API_KEY" in st.secrets or
            os.path.exists('.env')
        )
        api_key_valid = os.environ.get('ANTHROPIC_API_KEY', '').startswith('sk-')
        
        if not api_key_set:
            st.warning("⚠️ Set your ANTHROPIC_API_KEY in `.streamlit/secrets.toml` or `.env` file!")
        elif not api_key_valid:
            st.warning("⚠️ Your API key appears to be a placeholder. Add your real key to `.streamlit/secrets.toml`")
        
        if st.button("🎯 Start Scoring", type="primary", key="score", disabled=len(unscored) == 0):
            with st.spinner(f"Scoring {len(unscored)} jobs... This may take a while."):
                venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
                output, success = run_command(f"{venv_python} main.py score")
                
                if success:
                    st.success("Scoring complete!")
                else:
                    st.warning("Scoring finished with some errors.")
                
                with st.expander("View Output"):
                    st.code(output)
                
                st.rerun()
    
    st.markdown("---")
    
    # Database management
    st.subheader("🗄️ Database")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reinitialize Database"):
            init_db()
            st.success("Database initialized!")
    
    with col2:
        st.download_button(
            "📥 Export Jobs (CSV)",
            data=pd.DataFrame([j.to_dict() for j in get_jobs(limit=10000)]).to_csv(index=False),
            file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col3:
        jobs = get_jobs(limit=10000)
        st.metric("Database Size", f"{len(jobs)} jobs")


# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Job Hunter v1.0 • Built with Streamlit")


