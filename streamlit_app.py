import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from database import (
    init_database, get_enabled_sports, get_api_config, cache_news, get_cached_news,
    get_all_available_apis, save_api_config, get_database_stats
)

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Real-Time Sports News Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .header {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .news-item {
        background: white;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .news-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .game-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .game-score {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .team-name {
        font-size: 1.2em;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .player-card {
        background: #f0f2f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .stat-box {
        background: white;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .news-title {
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        font-size: 1.1em;
    }
    .news-meta {
        font-size: 0.9em;
        color: #666;
    }
    .news-description {
        color: #444;
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    .live-badge {
        background: #ff4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .api-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-badge {
        background: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

if 'newsapi_key' not in st.session_state:
    api_config = get_api_config("newsapi")
    st.session_state.newsapi_key = api_config[0] if api_config else None

if 'active_apis' not in st.session_state:
    st.session_state.active_apis = {}

# Header
st.markdown('<div class="header">⚽ Real-Time Sports News Dashboard 🏆</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Dashboard Settings")

# API Configuration Section
with st.sidebar.expander("🔑 API Configuration", expanded=True):
    st.info("📌 **Get FREE API keys - No credit card needed!**")
    
    # Tabs for different API sections
    api_tab1, api_tab2 = st.tabs(["Add Keys", "Available APIs"])
    
    with api_tab1:
        st.subheader("Add Your API Keys")
        
        # NewsAPI Key Input
        st.write("**1️⃣ NewsAPI (Recommended)**")
        st.caption("📰 Best for sports news articles")
        newsapi_key_input = st.text_input(
            "NewsAPI Key:",
            type="password",
            placeholder="abc123def456...",
            help="Get FREE at https://newsapi.org"
        )
        
        if newsapi_key_input:
            if st.button("✅ Save NewsAPI Key"):
                save_api_config("newsapi", newsapi_key_input, True)
                st.session_state.newsapi_key = newsapi_key_input
                st.success("✅ NewsAPI Key Saved!")
                st.balloons()
        
        st.divider()
        
        # TheSportsDB Key Input
        st.write("**2️⃣ TheSportsDB (Optional)**")
        st.caption("🏆 For team & player stats")
        thesportsdb_key_input = st.text_input(
            "TheSportsDB Key:",
            type="password",
            placeholder="xyz789abc123...",
            help="Get FREE at https://www.thesportsdb.com"
        )
        
        if thesportsdb_key_input:
            if st.button("✅ Save TheSportsDB Key"):
                save_api_config("thesportsdb", thesportsdb_key_input, True)
                st.success("✅ TheSportsDB Key Saved!")
        
        st.divider()
        
        # Football-Data Key Input
        st.write("**3️⃣ Football-Data (Optional)**")
        st.caption("⚽ For football standings & results")
        footballdata_key_input = st.text_input(
            "Football-Data Key:",
            type="password",
            placeholder="key123abc...",
            help="Get FREE at https://www.football-data.org"
        )
        
        if footballdata_key_input:
            if st.button("✅ Save Football-Data Key"):
                save_api_config("footballdata", footballdata_key_input, True)
                st.success("✅ Football-Data Key Saved!")
        
        st.divider()
        
        # API Status
        st.subheader("📡 Active API Keys")
        col1, col2, col3 = st.columns(3)
        
        newsapi = get_api_config("newsapi")
        thesportsdb = get_api_config("thesportsdb")
        footballdata = get_api_config("footballdata")
        
        with col1:
            if newsapi:
                st.markdown("<div class='success-badge'>✅ NewsAPI</div>", unsafe_allow_html=True)
            else:
                st.write("❌ NewsAPI")
        
        with col2:
            if thesportsdb:
                st.markdown("✅ TheSportsDB")
            else:
                st.write("❌ TheSportsDB")
        
        with col3:
            if footballdata:
                st.markdown("✅ Football-Data")
            else:
                st.write("❌ Football-Data")
        
        st.markdown("---")
        
        # Current Status
        if newsapi:
            st.markdown(f"**Status:** 🟢 LIVE MODE - Using Real Data")
            st.session_state.newsapi_key = newsapi[0]
        else:
            st.markdown(f"**Status:** 🟡 DEMO MODE - Using Sample Data")
    
    with api_tab2:
        st.subheader("Available APIs")
        available_apis = get_all_available_apis()
        
        for api_name, api_info in available_apis.items():
            st.write(f"### {api_name} {api_info['rating']}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.caption(f"📊 {api_info['features']}")
                st.caption(f"📈 Limit: {api_info['limit']}")
            
            with col2:
                if st.button(f"Get Key →", key=f"api_{api_name}"):
                    st.write(f"Visit: {api_info['url']}")
            
            st.divider()

# Sport selection
available_sports = get_enabled_sports()
sport_list = [f"{emoji} {name}" for _, name, emoji, _ in available_sports]

selected_sports = st.sidebar.multiselect(
    "🏅 Select Sports to Display",
    sport_list,
    default=sport_list[:3] if sport_list else []
)

# Refresh settings
col1, col2 = st.sidebar.columns(2)
with col1:
    refresh_interval = st.slider("Refresh interval (minutes)", 5, 60, 15)
with col2:
    if st.button("🔄 Refresh Now"):
        st.session_state.last_refresh = datetime.now()
        st.cache_clear()
        st.rerun()

st.sidebar.markdown("---")

# Dashboard Stats
st.sidebar.subheader("📊 Dashboard Stats")
db_stats = get_database_stats()

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Games", db_stats.get('games', 0))
with col2:
    st.metric("Players", db_stats.get('players', 0))

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Teams", db_stats.get('team_stats', 0))
with col2:
    st.metric("Cached News", db_stats.get('news_cache', 0))

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.markdown(f"**Total Sports:** {len(available_sports)}")

# Mock data for games and stats
def get_mock_games(sport_keyword):
    """Get mock game data"""
    games_data = {
        "football": [
            {"home": "Manchester United", "away": "Liverpool", "score_home": 2, "score_away": 1, "date": "2 days ago", "status": "Completed"},
            {"home": "Arsenal", "away": "Chelsea", "score_home": 3, "score_away": 2, "date": "1 day ago", "status": "Completed"},
            {"home": "City", "away": "Tottenham", "score_home": 4, "score_away": 0, "date": "Today", "status": "Completed"},
        ],
        "nba": [
            {"home": "Lakers", "away": "Celtics", "score_home": 112, "score_away": 108, "date": "1 day ago", "status": "Completed"},
            {"home": "Warriors", "away": "Suns", "score_home": 120, "score_away": 115, "date": "2 days ago", "status": "Completed"},
            {"home": "Heat", "away": "Bucks", "score_home": 105, "score_away": 110, "date": "3 days ago", "status": "Completed"},
        ],
        "cricket": [
            {"home": "India", "away": "Australia", "score_home": 285, "score_away": 245, "date": "1 day ago", "status": "Completed"},
            {"home": "England", "away": "Pakistan", "score_home": 320, "score_away": 298, "date": "2 days ago", "status": "Completed"},
            {"home": "South Africa", "away": "New Zealand", "score_home": 275, "score_away": 260, "date": "3 days ago", "status": "Completed"},
        ],
        "tennis": [
            {"home": "Novak Djokovic", "away": "Carlos Alcaraz", "score_home": "6-4", "score_away": "6-3", "date": "1 day ago", "status": "Completed"},
            {"home": "Rafael Nadal", "away": "Jannik Sinner", "score_home": "6-3", "score_away": "6-4", "date": "2 days ago", "status": "Completed"},
        ],
    }
    return games_data.get(sport_keyword.lower().replace(" racing", ""), [])

def get_mock_team_stats(sport_keyword):
    """Get mock team performance stats"""
    stats_data = {
        "football": [
            {"team": "Manchester United", "wins": 18, "draws": 4, "losses": 3, "goals": 62, "against": 28, "points": 58},
            {"team": "Liverpool", "wins": 19, "draws": 2, "losses": 4, "goals": 68, "against": 25, "points": 59},
            {"team": "Arsenal", "wins": 20, "draws": 1, "losses": 4, "goals": 71, "against": 26, "points": 61},
            {"team": "City", "wins": 21, "draws": 2, "losses": 2, "goals": 79, "against": 18, "points": 65},
        ],
        "nba": [
            {"team": "Celtics", "wins": 45, "losses": 12, "avg_points": 118.5, "avg_points_against": 109.2},
            {"team": "Lakers", "wins": 43, "losses": 14, "avg_points": 117.3, "avg_points_against": 110.8},
            {"team": "Warriors", "wins": 41, "losses": 16, "avg_points": 116.8, "avg_points_against": 111.5},
            {"team": "Suns", "wins": 40, "losses": 17, "avg_points": 115.2, "avg_points_against": 108.9},
        ],
        "cricket": [
            {"team": "India", "matches": 25, "wins": 18, "losses": 5, "draws": 2, "runs": 8520, "avg_runs": 340.8},
            {"team": "Australia", "matches": 25, "wins": 17, "losses": 6, "draws": 2, "runs": 8340, "avg_runs": 333.6},
            {"team": "England", "matches": 24, "wins": 16, "losses": 6, "draws": 2, "runs": 8100, "avg_runs": 337.5},
        ],
    }
    return stats_data.get(sport_keyword.lower().replace(" racing", ""), [])

def get_mock_top_players(sport_keyword):
    """Get mock top player stats"""
    players_data = {
        "football": [
            {"name": "Erling Haaland", "team": "City", "goals": 28, "assists": 8, "matches": 32},
            {"name": "Harry Kane", "team": "Bayern Munich", "goals": 25, "assists": 6, "matches": 30},
            {"name": "Cristiano Ronaldo", "team": "Al Nassr", "goals": 22, "assists": 5, "matches": 28},
        ],
        "nba": [
            {"name": "Luka Dončić", "team": "Mavericks", "points": 33.9, "rebounds": 9.2, "assists": 8.1},
            {"name": "LeBron James", "team": "Lakers", "points": 25.7, "rebounds": 8.3, "assists": 9.4},
            {"name": "Giannis Antetokounmpo", "team": "Bucks", "points": 31.1, "rebounds": 11.8, "assists": 6.2},
        ],
        "cricket": [
            {"name": "Virat Kohli", "team": "India", "runs": 1850, "avg": 52.14, "centuries": 4},
            {"name": "Steve Smith", "team": "Australia", "runs": 1720, "avg": 51.51, "centuries": 3},
            {"name": "Joe Root", "team": "England", "runs": 1680, "avg": 50.12, "centuries": 3},
        ],
        "tennis": [
            {"name": "Carlos Alcaraz", "rank": 1, "titles": 3, "win_rate": "82%"},
            {"name": "Novak Djokovic", "rank": 2, "titles": 2, "win_rate": "78%"},
            {"name": "Jannik Sinner", "rank": 3, "titles": 2, "win_rate": "76%"},
        ],
    }
    return players_data.get(sport_keyword.lower().replace(" racing", ""), [])

# API Functions
@st.cache_data(ttl=300)
def get_live_sports_news(keyword, api_key):
    """Fetch LIVE news from NewsAPI"""
    if not api_key or api_key.strip() == "":
        return None
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": keyword,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": api_key.strip()
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "error":
                st.error(f"❌ API Error: {data.get('message', 'Unknown error')}")
                return None
            
            articles = data.get("articles", [])
            
            if not articles:
                st.warning(f"No news found for {keyword}")
                return None
            
            news_items = []
            for article in articles:
                news_items.append({
                    "title": article.get("title", "N/A"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "time": format_time(article.get("publishedAt")),
                    "description": article.get("description", ""),
                    "url": article.get("url", "#"),
                })
            return news_items
        else:
            st.error(f"❌ API Error {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error fetching news: {str(e)}")
        return None

def format_time(iso_string):
    """Format ISO time to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        diff = datetime.now(dt.tzinfo) - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes} min{'s' if minutes > 1 else ''} ago"
        return "Just now"
    except:
        return "Recently"

# Display sections
def display_recent_games(sport_keyword):
    """Display recent games"""
    st.subheader("🎮 Recent Games")
    games = get_mock_games(sport_keyword)
    
    if games:
        for game in games:
            with st.container():
                st.markdown(f"<div class='game-card'>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.markdown(f"<div class='team-name'>{game['home']}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<div class='game-score'>{game['score_home']} - {game['score_away']}</div>", unsafe_allow_html=True)
                    st.caption(f"📅 {game['date']}")
                
                with col3:
                    st.markdown(f"<div class='team-name'>{game['away']}</div>", unsafe_allow_html=True)
                
                st.markdown(f"</div>", unsafe_allow_html=True)
    else:
        st.info("No recent games available")

def display_team_performance(sport_keyword):
    """Display team performance stats"""
    st.subheader("📊 Team Performance")
    stats = get_mock_team_stats(sport_keyword)
    
    if stats:
        if sport_keyword.lower() == "nba":
            df = pd.DataFrame(stats)
            df = df[['team', 'wins', 'losses', 'avg_points', 'avg_points_against']]
            df.columns = ['Team', 'Wins', 'Losses', 'Avg Points', 'Avg Against']
        elif sport_keyword.lower() == "cricket":
            df = pd.DataFrame(stats)
            df = df[['team', 'matches', 'wins', 'losses', 'runs', 'avg_runs']]
            df.columns = ['Team', 'Matches', 'Wins', 'Losses', 'Runs', 'Avg Runs']
        else:
            df = pd.DataFrame(stats)
            df = df[['team', 'wins', 'draws', 'losses', 'goals', 'points']]
            df.columns = ['Team', 'Wins', 'Draws', 'Losses', 'Goals', 'Points']
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No team stats available")

def display_top_players(sport_keyword):
    """Display top players"""
    st.subheader("⭐ Best Players")
    players = get_mock_top_players(sport_keyword)
    
    if players:
        for idx, player in enumerate(players, 1):
            st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
            st.markdown(f"**{idx}. {player['name']}** - {player.get('team', player.get('rank', ''))}")
            
            stats_text = " | ".join([f"{k}: {v}" for k, v in player.items() if k not in ['name', 'team', 'rank']])
            st.caption(stats_text)
            st.markdown(f"</div>", unsafe_allow_html=True)
    else:
        st.info("No player stats available")

def display_news(sport_name, sport_key):
    """Display news"""
    st.subheader("📰 Latest News")
    
    with st.spinner(f"Fetching {sport_name} news..."):
        news_items = None
        
        if st.session_state.newsapi_key:
            news_items = get_live_sports_news(sport_key, st.session_state.newsapi_key)
        
        if news_items is None:
            st.info("📡 Using sample data (Add API key in sidebar for live news)")
            news_items = [{"title": "Sample News - Add NewsAPI Key for Live Updates", "source": "Demo", "time": "now", "description": "Click 🔑 API Configuration in sidebar to add your free NewsAPI key", "url": "#"}]
        
        if news_items:
            for idx, item in enumerate(news_items, 1):
                col1, col2 = st.columns([0.85, 0.15])
                
                with col1:
                    st.markdown(f"<div class='news-item'>", unsafe_allow_html=True)
                    
                    if st.session_state.newsapi_key:
                        st.markdown(f"<div class='news-title'><span class='live-badge'>🔴 LIVE</span> {idx}. {item['title']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='news-title'>{idx}. {item['title']}</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div class='news-meta'>📰 {item['source']} • ⏰ {item['time']}</div>", unsafe_allow_html=True)
                    
                    if item.get('description'):
                        st.markdown(f"<div class='news-description'>{item['description'][:200]}...</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"</div>", unsafe_allow_html=True)
                
                with col2:
                    if item.get('url') and item['url'] != "#":
                        st.markdown(f"[🔗 Read]({item['url']})")

# Main content
st.markdown("---")

if selected_sports:
    sport_map = {f"{emoji} {name}": (keyword, emoji) for _, name, emoji, keyword in available_sports}
    
    tabs = st.tabs(selected_sports)
    
    for tab, sport in zip(tabs, selected_sports):
        with tab:
            if sport in sport_map:
                keyword, emoji = sport_map[sport]
                sport_name = sport.replace(emoji, "").strip()
                
                st.subheader(f"{emoji} {sport_name}")
                
                sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["📰 News", "🎮 Games", "📊 Stats", "⭐ Players"])
                
                with sub_tab1:
                    display_news(sport_name, keyword)
                
                with sub_tab2:
                    display_recent_games(keyword)
                
                with sub_tab3:
                    display_team_performance(keyword)
                
                with sub_tab4:
                    display_top_players(keyword)

else:
    st.warning("👈 Please select at least one sport from the sidebar")

# Footer
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.newsapi_key:
        st.metric("Data Source", "🟢 LIVE")
    else:
        st.metric("Data Source", "🟡 DEMO")

with col2:
    st.metric("Last Refresh", st.session_state.last_refresh.strftime('%H:%M:%S'))

with col3:
    st.metric("Sports Available", len(available_sports))

st.markdown("""
---
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    📊 Real-Time Sports News Dashboard with CMS<br>
    🔴 Add your API keys in the sidebar for LIVE sports news!<br>
    ⚙️ Manage sports in Admin Panel<br>
    <br>
    <strong>Get Free API Keys:</strong><br>
    🔗 <a href="https://newsapi.org/" target="_blank">NewsAPI</a> | 
    🔗 <a href="https://www.thesportsdb.com/" target="_blank">TheSportsDB</a> | 
    🔗 <a href="https://www.football-data.org/" target="_blank">Football-Data</a>
</div>
""", unsafe_allow_html=True)