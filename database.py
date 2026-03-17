import sqlite3
import os
from datetime import datetime

DB_FILE = "sports_cms.db"

def init_database():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Sports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            emoji TEXT NOT NULL,
            keyword TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # News Sources table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            sport_id INTEGER,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sport_id) REFERENCES sports(id)
        )
    ''')
    
    # API Configuration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT UNIQUE NOT NULL,
            api_key TEXT,
            enabled BOOLEAN DEFAULT 1,
            requests_today INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            game_date TIMESTAMP,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sport_id) REFERENCES sports(id)
        )
    ''')
    
    # Team Stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER,
            team_name TEXT NOT NULL,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            avg_points REAL DEFAULT 0,
            avg_points_against REAL DEFAULT 0,
            matches INTEGER DEFAULT 0,
            runs INTEGER DEFAULT 0,
            avg_runs REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sport_id) REFERENCES sports(id)
        )
    ''')
    
    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER,
            name TEXT NOT NULL,
            team TEXT NOT NULL,
            position TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0,
            points REAL DEFAULT 0,
            rebounds REAL DEFAULT 0,
            assists_count REAL DEFAULT 0,
            runs INTEGER DEFAULT 0,
            average REAL DEFAULT 0,
            centuries INTEGER DEFAULT 0,
            rank INTEGER,
            titles INTEGER DEFAULT 0,
            win_rate TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sport_id) REFERENCES sports(id)
        )
    ''')
    
    # News Cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER,
            title TEXT NOT NULL,
            source TEXT,
            description TEXT,
            url TEXT UNIQUE,
            image_url TEXT,
            published_at TIMESTAMP,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sport_id) REFERENCES sports(id)
        )
    ''')
    
    # Dashboard Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dashboard_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Insert default data if empty
    cursor.execute('SELECT COUNT(*) FROM sports')
    if cursor.fetchone()[0] == 0:
        insert_default_sports(conn)
    
    conn.close()

def insert_default_sports(conn):
    """Insert default sports data"""
    cursor = conn.cursor()
    default_sports = [
        ("Football (Soccer)", "⚽", "football"),
        ("Cricket", "🏏", "cricket"),
        ("American Football", "🏈", "american football"),
        ("NBA", "🏀", "nba"),
        ("F1 Racing", "🏎️", "f1"),
        ("Tennis", "🎾", "tennis"),
        ("Olympics", "🏅", "olympics"),
    ]
    cursor.executemany('INSERT INTO sports (name, emoji, keyword) VALUES (?, ?, ?)', default_sports)
    conn.commit()

# ==================== SPORTS MANAGEMENT ====================

def get_all_sports():
    """Get all sports from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, emoji, keyword, enabled FROM sports ORDER BY name')
    sports = cursor.fetchall()
    conn.close()
    return sports

def get_enabled_sports():
    """Get enabled sports only"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, emoji, keyword FROM sports WHERE enabled = 1 ORDER BY name')
    sports = cursor.fetchall()
    conn.close()
    return sports

def add_sport(name, emoji, keyword):
    """Add new sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sports (name, emoji, keyword) VALUES (?, ?, ?)',
            (name, emoji, keyword)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error adding sport: {e}")
        return False

def update_sport(sport_id, enabled):
    """Enable/disable sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE sports SET enabled = ? WHERE id = ?', (enabled, sport_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating sport: {e}")
        return False

def delete_sport(sport_id):
    """Delete sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sports WHERE id = ?', (sport_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting sport: {e}")
        return False

# ==================== API CONFIGURATION ====================

def get_api_config(api_name):
    """Get API configuration"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT api_key, enabled FROM api_config WHERE api_name = ?', (api_name,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Error getting API config: {e}")
        return None

def save_api_config(api_name, api_key, enabled=True):
    """Save API configuration"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO api_config (api_name, api_key, enabled, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (api_name, api_key, enabled, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving API config: {e}")
        return False

def add_api_key(api_name, api_key, api_url=None, limit=None):
    """Add new API key to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if API key already exists
        cursor.execute('SELECT id FROM api_config WHERE api_name = ?', (api_name,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing key
            cursor.execute('''
                UPDATE api_config 
                SET api_key = ?, enabled = 1, last_updated = ?
                WHERE api_name = ?
            ''', (api_key, datetime.now(), api_name))
        else:
            # Insert new key
            cursor.execute('''
                INSERT INTO api_config (api_name, api_key, enabled, last_updated)
                VALUES (?, ?, 1, ?)
            ''', (api_name, api_key, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding API key: {e}")
        return False

def delete_api_key(api_name):
    """Delete API key from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM api_config WHERE api_name = ?', (api_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting API key: {e}")
        return False

def is_api_key_valid(api_name, api_key):
    """Check if API key is valid (basic validation)"""
    if not api_key or len(api_key.strip()) < 5:
        return False
    return True

def get_api_key_status(api_name):
    """Get status of API key"""
    try:
        config = get_api_config(api_name)
        if config:
            api_key, enabled = config
            return {
                "configured": True,
                "enabled": enabled,
                "masked_key": f"{api_key[:5]}...{api_key[-5:]}" if api_key else None
            }
        return {"configured": False, "enabled": False, "masked_key": None}
    except Exception as e:
        print(f"Error getting API status: {e}")
        return {"configured": False, "enabled": False, "masked_key": None}

def enable_api_key(api_name):
    """Enable API key"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE api_config SET enabled = 1 WHERE api_name = ?', (api_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error enabling API key: {e}")
        return False

def disable_api_key(api_name):
    """Disable API key"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE api_config SET enabled = 0 WHERE api_name = ?', (api_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error disabling API key: {e}")
        return False

def get_all_api_configs():
    """Get all API configurations"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT api_name, api_key, enabled FROM api_config ORDER BY api_name')
        configs = cursor.fetchall()
        conn.close()
        return configs
    except Exception as e:
        print(f"Error getting API configs: {e}")
        return []
    
def get_all_available_apis():
    """Get list of available APIs with their info"""
    apis = {
        "NewsAPI": {
            "url": "https://newsapi.org/",
            "limit": "100/day",
            "features": "News articles, real-time updates",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "TheSportsDB": {
            "url": "https://www.thesportsdb.com/",
            "limit": "1000/day",
            "features": "Teams, players, events, images",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "Football-Data": {
            "url": "https://www.football-data.org/",
            "limit": "600/month",
            "features": "Football standings, results",
            "rating": "⭐⭐⭐⭐"
        },
        "ESPN": {
            "url": "https://www.espn.com/apis/",
            "limit": "Unlimited",
            "features": "Live scores, standings, stats",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "RapidAPI": {
            "url": "https://rapidapi.com/",
            "limit": "50-100/day",
            "features": "Multiple sports, aggregated",
            "rating": "⭐⭐⭐⭐"
        }
    }
    return apis

def get_all_available_apis():
    """Get list of available APIs with their info"""
    apis = {
        "NewsAPI": {
            "url": "https://newsapi.org/",
            "limit": "100/day",
            "features": "News articles, real-time updates",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "TheSportsDB": {
            "url": "https://www.thesportsdb.com/",
            "limit": "1000/day",
            "features": "Teams, players, events, images",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "Football-Data": {
            "url": "https://www.football-data.org/",
            "limit": "600/month",
            "features": "Football standings, results",
            "rating": "⭐⭐⭐⭐"
        },
        "ESPN": {
            "url": "https://www.espn.com/apis/",
            "limit": "Unlimited",
            "features": "Live scores, standings, stats",
            "rating": "⭐⭐⭐⭐⭐"
        },
        "RapidAPI": {
            "url": "https://rapidapi.com/",
            "limit": "50-100/day",
            "features": "Multiple sports, aggregated",
            "rating": "⭐⭐⭐⭐"
        }
    }
    return apis

# ==================== GAMES MANAGEMENT ====================

def add_game(sport_id, home_team, away_team, home_score, away_score, game_date, status):
    """Add new game"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (sport_id, home_team, away_team, home_score, away_score, game_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sport_id, home_team, away_team, home_score, away_score, game_date, status))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding game: {e}")
        return False

def get_recent_games(sport_id, limit=10):
    """Get recent games for a sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, home_team, away_team, home_score, away_score, game_date, status
            FROM games WHERE sport_id = ?
            ORDER BY game_date DESC LIMIT ?
        ''', (sport_id, limit))
        games = cursor.fetchall()
        conn.close()
        return games
    except Exception as e:
        print(f"Error getting games: {e}")
        return []

def delete_game(game_id):
    """Delete game"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting game: {e}")
        return False

# ==================== TEAM STATS MANAGEMENT ====================

def add_or_update_team_stats(sport_id, team_name, **kwargs):
    """Add or update team stats"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if team exists
        cursor.execute('SELECT id FROM team_stats WHERE sport_id = ? AND team_name = ?', (sport_id, team_name))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            update_fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            update_fields += ", updated_at = ?"
            values = list(kwargs.values()) + [datetime.now(), sport_id, team_name]
            cursor.execute(f'UPDATE team_stats SET {update_fields} WHERE sport_id = ? AND team_name = ?', values)
        else:
            # Insert new
            fields = ", ".join(kwargs.keys())
            placeholders = ", ".join(["?" for _ in kwargs])
            values = list(kwargs.values())
            cursor.execute(f'''
                INSERT INTO team_stats (sport_id, team_name, {fields})
                VALUES (?, ?, {placeholders})
            ''', [sport_id, team_name] + values)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating team stats: {e}")
        return False

def get_team_stats(sport_id):
    """Get team stats for a sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM team_stats WHERE sport_id = ?
            ORDER BY points DESC
        ''', (sport_id,))
        stats = cursor.fetchall()
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting team stats: {e}")
        return []

# ==================== PLAYERS MANAGEMENT ====================

def add_or_update_player(sport_id, name, team, **kwargs):
    """Add or update player stats"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if player exists
        cursor.execute('SELECT id FROM players WHERE sport_id = ? AND name = ? AND team = ?', (sport_id, name, team))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            update_fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            update_fields += ", updated_at = ?"
            values = list(kwargs.values()) + [datetime.now(), sport_id, name, team]
            cursor.execute(f'UPDATE players SET {update_fields} WHERE sport_id = ? AND name = ? AND team = ?', values)
        else:
            # Insert new
            fields = ", ".join(kwargs.keys())
            placeholders = ", ".join(["?" for _ in kwargs])
            values = list(kwargs.values())
            cursor.execute(f'''
                INSERT INTO players (sport_id, name, team, {fields})
                VALUES (?, ?, ?, {placeholders})
            ''', [sport_id, name, team] + values)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating player: {e}")
        return False

def get_top_players(sport_id, limit=10):
    """Get top players for a sport"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM players WHERE sport_id = ?
            ORDER BY goals DESC, points DESC, rank ASC LIMIT ?
        ''', (sport_id, limit))
        players = cursor.fetchall()
        conn.close()
        return players
    except Exception as e:
        print(f"Error getting players: {e}")
        return []

# ==================== NEWS CACHE MANAGEMENT ====================

def cache_news(sport_id, title, source, description, url, image_url=None, published_at=None):
    """Cache news articles"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO news_cache 
            (sport_id, title, source, description, url, image_url, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sport_id, title, source, description, url, image_url, published_at))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error caching news: {e}")
        return False

def get_cached_news(sport_id, hours=24, limit=10):
    """Get cached news"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, source, description, url, image_url, published_at FROM news_cache
            WHERE sport_id = ? AND cached_at > datetime('now', '-' || ? || ' hours')
            ORDER BY published_at DESC LIMIT ?
        ''', (sport_id, hours, limit))
        news = cursor.fetchall()
        conn.close()
        return news
    except Exception as e:
        print(f"Error getting cached news: {e}")
        return []

def clear_old_cache(hours=168):
    """Clear old cached news (default: 1 week)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM news_cache WHERE cached_at < datetime('now', '-' || ? || ' hours')
        ''', (hours,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False

# ==================== DASHBOARD SETTINGS ====================

def get_setting(setting_name, default_value=None):
    """Get dashboard setting"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT setting_value FROM dashboard_settings WHERE setting_name = ?', (setting_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default_value
    except Exception as e:
        print(f"Error getting setting: {e}")
        return default_value

def set_setting(setting_name, setting_value):
    """Set dashboard setting"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO dashboard_settings (setting_name, setting_value, updated_at)
            VALUES (?, ?, ?)
        ''', (setting_name, setting_value, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error setting value: {e}")
        return False

def get_all_settings():
    """Get all dashboard settings"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT setting_name, setting_value FROM dashboard_settings')
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return settings
    except Exception as e:
        print(f"Error getting settings: {e}")
        return {}

# ==================== DATABASE UTILITIES ====================

def get_database_size():
    """Get database file size in MB"""
    try:
        if os.path.exists(DB_FILE):
            size_bytes = os.path.getsize(DB_FILE)
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        return 0
    except Exception as e:
        print(f"Error getting database size: {e}")
        return 0

def reset_database():
    """Reset entire database"""
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_database()
        return True
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False

def backup_database():
    """Create database backup"""
    try:
        import shutil
        backup_file = f"sports_cms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(DB_FILE, backup_file)
        return backup_file
    except Exception as e:
        print(f"Error backing up database: {e}")
        return None

def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        stats = {}
        tables = ['sports', 'games', 'team_stats', 'players', 'news_cache', 'api_config']
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats[table] = count
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}

# ==================== NEWS SOURCES MANAGEMENT ====================

def add_news_source(name, sport_id):
    """Add news source"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO news_sources (name, sport_id) VALUES (?, ?)',
            (name, sport_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error adding news source: {e}")
        return False

def get_news_sources(sport_id=None):
    """Get news sources"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if sport_id:
            cursor.execute('SELECT id, name, sport_id, enabled FROM news_sources WHERE sport_id = ?', (sport_id,))
        else:
            cursor.execute('SELECT id, name, sport_id, enabled FROM news_sources ORDER BY name')
        
        sources = cursor.fetchall()
        conn.close()
        return sources
    except Exception as e:
        print(f"Error getting news sources: {e}")
        return []

def update_news_source(source_id, enabled):
    """Update news source status"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE news_sources SET enabled = ? WHERE id = ?', (enabled, source_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating news source: {e}")
        return False

def delete_news_source(source_id):
    """Delete news source"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM news_sources WHERE id = ?', (source_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting news source: {e}")
        return False