import sqlite3
import hashlib
import os
import json
from datetime import datetime

if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    import shutil
    DB_DIR = '/tmp'
    DB_FILE = os.path.join(DB_DIR, 'ecoplanet.db')
    bundled_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecoplanet.db')
    if os.path.exists(bundled_db) and not os.path.exists(DB_FILE):
        try:
            shutil.copy2(bundled_db, DB_FILE)
        except Exception:
            pass
else:
    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecoplanet.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table (Admin & Registered Community Members)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            full_name TEXT,
            city TEXT,
            focus_area TEXT DEFAULT 'General',
            avatar TEXT DEFAULT '🌱',
            terms_accepted INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure all user columns exist (migration for existing database)
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row['name'] for row in cursor.fetchall()]
    migration_cols = [
        ('full_name', 'TEXT'),
        ('city', 'TEXT'),
        ('focus_area', "TEXT DEFAULT 'General'"),
        ('avatar', "TEXT DEFAULT '🌱'"),
        ('terms_accepted', 'INTEGER DEFAULT 1')
    ]
    for col_name, col_def in migration_cols:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass

    # 1b. Persistent User Sessions Table (Database for Remember Me Logins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            remember_me INTEGER DEFAULT 1,
            ip_address TEXT,
            user_agent TEXT,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 1c. User Eco Actions Table (Dashboard Activity Logging)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_eco_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            title TEXT NOT NULL,
            impact_metric REAL NOT NULL,
            unit TEXT NOT NULL,
            notes TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 1d. OTP Verifications Table (Two-Factor and Email Code Verification)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            purpose TEXT NOT NULL,
            pending_payload TEXT,
            attempts INTEGER DEFAULT 0,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Feedback Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            event_date TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            organizer TEXT NOT NULL,
            capacity INTEGER DEFAULT 100,
            registered_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Event Registrations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            tickets INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    ''')

    # 5. Articles & News Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            read_time TEXT DEFAULT '4 min read',
            published_date TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 6. Environmental Pledges Table ("One Planet, One Responsibility")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pledges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            pledges_list TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. Newsletter Subscribers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 8. Environmental Statistics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            unit TEXT NOT NULL,
            label TEXT NOT NULL,
            source TEXT
        )
    ''')

    # 9. Calculation History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calc_type TEXT NOT NULL,
            result_metric REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure calculations has user_id column
    cursor.execute("PRAGMA table_info(calculations)")
    calc_cols = [row['name'] for row in cursor.fetchall()]
    if 'user_id' not in calc_cols:
        try:
            cursor.execute("ALTER TABLE calculations ADD COLUMN user_id INTEGER")
        except Exception:
            pass

    # Ensure pledges has user_id column
    cursor.execute("PRAGMA table_info(pledges)")
    pledge_cols = [row['name'] for row in cursor.fetchall()]
    if 'user_id' not in pledge_cols:
        try:
            cursor.execute("ALTER TABLE pledges ADD COLUMN user_id INTEGER")
        except Exception:
            pass

    conn.commit()

    # Seed Initial Data if empty
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()

    # Seed Admin User (admin / admin123)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        admin_pass = hash_password("admin123")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, city, focus_area, avatar, terms_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@ecoprotect.org', admin_pass, 'admin', 'Platform Administrator', 'Global Control Center', 'Climate Governance', '🛡️', 1))

    # Seed Event Organiser User (organizer / org123)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'organizer'")
    if cursor.fetchone()[0] == 0:
        org_pass = hash_password("org123")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, city, focus_area, avatar, terms_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('organizer', 'organizer@ecoprotect.org', org_pass, 'organizer', 'Marcus Thorne (Green Earth)', 'Portland, OR', 'Forests & Marine Cleanups', '📅', 1))

    # Seed Participant User (participant / part123)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'participant'")
    if cursor.fetchone()[0] == 0:
        part_pass = hash_password("part123")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, city, focus_area, avatar, terms_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('participant', 'participant@ecoprotect.org', part_pass, 'participant', 'Aria Chen', 'San Francisco, CA', 'Renewable Energy & Forests', '🌿', 1))

    # Also keep ecouser alias (ecouser / eco123)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'ecouser'")
    if cursor.fetchone()[0] == 0:
        demo_pass = hash_password("eco123")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, city, focus_area, avatar, terms_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ecouser', 'guardian@ecoprotect.org', demo_pass, 'participant', 'Aria Chen', 'San Francisco, CA', 'Renewable Energy & Forests', '🌱', 1))

    # Seed Core Statistics
    stats_data = [
        ('forest_cover', '31.2', '%', 'Global Land Forest Coverage', 'UN FAO Global Forest Resources'),
        ('clean_energy', '30.2', '%', 'Global Renewable Electricity Share', 'International Energy Agency (IEA)'),
        ('carbon_ppm', '422.5', 'ppm', 'Atmospheric CO2 Concentration', 'NOAA Mauna Loa Observatory'),
        ('ocean_plastic', '14.0', 'M Tonnes', 'Plastic Entering Oceans Annually', 'IUCN Ocean Plastics Assessment'),
        ('pledges_count', '12480', 'Pledges', 'Global Citizens Pledged', 'EcoProtect Community'),
        ('trees_planted', '58240', 'Trees', 'Trees Planted Through Initiatives', 'Green Canopy Project')
    ]
    for key, val, unit, label, source in stats_data:
        cursor.execute('''
            INSERT OR IGNORE INTO stats (key, value, unit, label, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, val, unit, label, source))

    # Seed Events
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        events_data = [
            (
                'Green Canopy 2026: 10,000 Tree Plantation Drive',
                'Afforestation',
                '2026-10-15',
                'Metro Riverside Eco Park & Nature Reserve',
                'Join thousands of volunteers to plant native saplings and restore vital riparian biodiversity buffers along our city river.',
                'Green Earth Foundation',
                500,
                142
            ),
            (
                'Coastal Ocean & Beach Plastic Clean-up',
                'Marine Conservation',
                '2026-10-28',
                'Silver Sands Public Coastline & Estuary',
                'A community-driven campaign to intercept marine debris, categorize single-use plastics for recycling, and protect coastal bird habitats.',
                'Ocean Care Coalition',
                300,
                88
            ),
            (
                'World Food & Water Day Sustainable Workshop',
                'Conservation & Lifestyle',
                '2026-11-12',
                'City Science & Environmental Center',
                'Hands-on masterclass covering rainwater harvesting installation, home composting techniques, and zero-waste kitchen meal planning.',
                'Urban Sustainability Council',
                150,
                65
            ),
            (
                'Youth Climate Action & Renewable Energy Summit',
                'Climate & Energy',
                '2026-11-25',
                'Convention Hall B & Virtual Livestream',
                'Featuring renewable energy scientists, student innovators showcasing solar gadgets, and workshops on local climate mitigation policy.',
                'Global Youth Climate Network',
                400,
                210
            )
        ]
        cursor.executemany('''
            INSERT INTO events (title, category, event_date, location, description, organizer, capacity, registered_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', events_data)

    # Seed Articles & News
    cursor.execute("SELECT COUNT(*) FROM articles")
    if cursor.fetchone()[0] == 0:
        articles_data = [
            (
                'The Rapid Evolution of Solar and Offshore Wind in 2026',
                'Renewable Energy',
                'Renewable energy capacity surges as next-generation perovskite solar panels and floating deep-sea wind turbines achieve historic grid parity.',
                'The global transition towards clean energy has accelerated dramatically in recent years. By combining high-efficiency perovskite tandem solar cells with gigawatt-scale offshore wind farms, renewable power sources now provide over 30% of global electricity generation. Countries investing in modernized smart grids and utility-scale battery energy storage systems (BESS) are demonstrating that reliable zero-carbon grids are not merely a future dream, but a present-day reality.',
                'Dr. Helena Vance',
                '5 min read',
                '2026-09-18',
                'solar_wind'
            ),
            (
                'Rethinking Plastics: From Microplastics to Circular Bio-Polymers',
                'Pollution Control',
                'Understanding the systemic journey of plastic waste through terrestrial ecosystems into marine food webs and how circular solutions offer a path forward.',
                'Microplastics—particles smaller than 5 millimeters—have now been discovered in mountain snowpacks, deep ocean trenches, and human bloodstreams. The primary drivers remain single-use packaging and synthetic fiber shedding. In response, scientists and progressive municipalities are moving beyond traditional recycling toward circular bio-polymers that naturally mineralize without toxic residue, coupled with extended producer responsibility (EPR) legislation.',
                'Marcus Thorne',
                '6 min read',
                '2026-09-12',
                'plastics_circular'
            ),
            (
                'Forests as Living Climate Shields: The Science of Afforestation',
                'Forest Conservation',
                'Why restoring biodiverse native forests is exponentially more effective for carbon sequestration and flood mitigation than monoculture plantations.',
                'Forests absorb roughly 2.6 billion tonnes of carbon dioxide each year, functioning as the planet’s green lungs. However, recent ecological studies emphasize that planting monoculture timber lots does not replicate the resilience of ancient old-growth ecosystems. Modern afforestation initiatives emphasize multi-layered native species, preserving mycorrhyzal soil networks, and empowering indigenous forest stewards to safeguard long-term biodiversity.',
                'Elena Rostova',
                '4 min read',
                '2026-09-05',
                'forest_shield'
            ),
            (
                'Household Water Security: Practical Rainwater Harvesting for Urban Homes',
                'Water Conservation',
                'How simple rooftop catchment, first-flush diversion, and sand filtration can cut municipal water dependence by up to 50%.',
                'Freshwater makes up less than 3% of all water on Earth, with accessible freshwater representing a fraction of 1%. Urban centers worldwide face declining aquifer tables. Modern residential rainwater harvesting systems capture rooftop precipitation, divert initial dust with automatic first-flush valves, and route purified water directly to irrigation, laundry, and toilet flushing—drastically lowering municipal strain.',
                'Tariq Al-Mansoor',
                '5 min read',
                '2026-08-28',
                'water_harvest'
            ),
            (
                'Biodiversity Hotspots: Protecting Our Planet’s Genetic Library',
                'Biodiversity',
                'Over 1 million species face extinction risk. Discover how ecological corridors and marine protected areas (MPAs) are restoring vanishing wildlife.',
                'From the Amazon basin to the coral reefs of the Coral Triangle, biodiversity hotspots support thousands of endemic species found nowhere else on Earth. Habitat fragmentation caused by road building and agricultural expansion represents the single greatest threat. By establishing continuous wildlife corridors and strictly enforced marine protected zones, conservationists are witnessing miraculous recoveries in keystone species.',
                'Dr. Sarah Jenkins',
                '7 min read',
                '2026-08-20',
                'biodiversity_hotspot'
            )
        ]
        cursor.executemany('''
            INSERT INTO articles (title, category, summary, content, author, read_time, published_date, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', articles_data)

    # Seed sample pledges
    cursor.execute("SELECT COUNT(*) FROM pledges")
    if cursor.fetchone()[0] == 0:
        sample_pledges = [
            ('Aria Chen', 'aria@example.com', 'San Francisco', 'save_water,reduce_plastic,plant_trees'),
            ('Liam O’Connor', 'liam@example.com', 'Dublin', 'public_transit,led_lighting,sort_waste'),
            ('Priya Sharma', 'priya@example.com', 'Bengaluru', 'plant_trees,solar_energy,reduce_plastic')
        ]
        cursor.executemany('''
            INSERT INTO pledges (name, email, city, pledges_list)
            VALUES (?, ?, ?, ?)
        ''', sample_pledges)

    conn.commit()

# ── USER AUTHENTICATION & SESSION PERSISTENCE ────────────────────────────────
import secrets
from datetime import datetime, timedelta

def register_user(username: str, email: str, password: str, full_name: str = '',
                  city: str = '', focus_area: str = 'General', terms_accepted: int = 1, role: str = 'participant'):
    """Registers a new user into the database with specific role (participant or organizer)."""
    username = username.strip().lower()
    email = email.strip().lower()
    if not username or not email or not password:
        return None, "Username, email, and password are required."
    
    if len(password) < 6:
        return None, "Password must be at least 6 characters long."
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Check uniqueness
    existing = cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
    if existing:
        conn.close()
        return None, "Username or email is already registered."
        
    pw_hash = hash_password(password)
    display_name = full_name.strip() if full_name.strip() else username.capitalize()
    
    # Assign icon based on role
    avatar = '🛡️' if role == 'admin' else ('📅' if role == 'organizer' else '🌿')
    user_role = 'organizer' if role == 'organizer' else ('admin' if role == 'admin' else 'participant')
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, full_name, city, focus_area, avatar, terms_accepted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, email, pw_hash, user_role, display_name, city.strip(), focus_area, avatar, terms_accepted))
    
    user_id = cursor.lastrowid
    
    # Seed welcome eco action
    cursor.execute('''
        INSERT INTO user_eco_actions (user_id, action_type, title, impact_metric, unit, notes)
        VALUES (?, 'community', 'Joined EcoProtect as ' || ?, 1.0, 'pledge', 'Account created & community terms accepted')
    ''', (user_id, user_role.capitalize()))
    
    conn.commit()
    conn.close()
    return user_id, None

def authenticate_user(identifier: str, password: str):
    """Authenticates a user via either username or email and verifies password hash."""
    identifier = identifier.strip().lower()
    pw_hash = hash_password(password)
    
    conn = get_db()
    user = conn.execute('''
        SELECT id, username, email, full_name, city, focus_area, avatar, role, terms_accepted, created_at
        FROM users
        WHERE (LOWER(username) = ? OR LOWER(email) = ?) AND password_hash = ?
    ''', (identifier, identifier, pw_hash)).fetchone()
    conn.close()
    
    return dict(user) if user else None

def create_user_session(user_id: int, remember_me: bool = True, ip_address: str = '', user_agent: str = ''):
    """Creates a persistent login session in the database so logins are remembered."""
    session_token = secrets.token_hex(32)
    # 30 days if remember_me, else 24 hours
    days = 30 if remember_me else 1
    expires_at = datetime.utcnow() + timedelta(days=days)
    expires_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, remember_me, ip_address, user_agent, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, session_token, 1 if remember_me else 0, ip_address, user_agent, expires_str))
    conn.commit()
    conn.close()
    
    return session_token, expires_at

def verify_user_session(session_token: str):
    """Verifies a remember token from database and returns the authenticated user."""
    if not session_token:
        return None
        
    conn = get_db()
    row = conn.execute('''
        SELECT u.id, u.username, u.email, u.full_name, u.city, u.focus_area, u.avatar, u.role, s.expires_at
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ?
    ''', (session_token,)).fetchone()
    conn.close()
    
    if not row:
        return None
        
    try:
        exp = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
        if exp < datetime.utcnow():
            delete_user_session(session_token)
            return None
    except Exception:
        pass
        
    return dict(row)

def delete_user_session(session_token: str):
    """Deletes a session token on logout."""
    if not session_token:
        return
    conn = get_db()
    conn.execute("DELETE FROM user_sessions WHERE session_token = ?", (session_token,))
    conn.commit()
    conn.close()

def get_user_by_id(user_id: int):
    """Retrieves user profile by ID."""
    conn = get_db()
    user = conn.execute('''
        SELECT id, username, email, full_name, city, focus_area, avatar, role, terms_accepted, created_at
        FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email: str):
    """Retrieves user profile by email address."""
    if not email:
        return None
    conn = get_db()
    user = conn.execute('''
        SELECT id, username, email, full_name, city, focus_area, avatar, role, terms_accepted, created_at
        FROM users WHERE LOWER(email) = LOWER(?)
    ''', (email.strip(),)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_identifier(identifier: str):
    """Retrieves user by either username or email address."""
    if not identifier:
        return None
    conn = get_db()
    clean = identifier.strip().lower()
    user = conn.execute('''
        SELECT id, username, email, full_name, city, focus_area, avatar, role, terms_accepted, created_at
        FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?
    ''', (clean, clean)).fetchone()
    conn.close()
    return dict(user) if user else None

def generate_otp(email: str, purpose: str = 'login', pending_payload: dict = None, expiry_minutes: int = 5) -> str:
    """Generates a secure 6-digit cryptographic OTP, cancels previous active OTPs for this email, and saves it."""
    email = email.strip().lower()
    otp_code = f"{secrets.randbelow(1000000):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    expires_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
    payload_json = json.dumps(pending_payload) if pending_payload else None
    
    conn = get_db()
    cursor = conn.cursor()
    # Invalidate prior active codes for this email and purpose
    cursor.execute("DELETE FROM otp_verifications WHERE LOWER(email) = ? AND purpose = ?", (email, purpose))
    cursor.execute('''
        INSERT INTO otp_verifications (email, otp_code, purpose, pending_payload, attempts, expires_at)
        VALUES (?, ?, ?, ?, 0, ?)
    ''', (email, otp_code, purpose, payload_json, expires_str))
    conn.commit()
    conn.close()
    return otp_code

def verify_otp(email: str, code: str, purpose: str = 'login'):
    """Verifies a 6-digit OTP code against the database. Returns (success: bool, message: str, pending_payload: dict)."""
    email = email.strip().lower()
    code = code.strip()
    
    conn = get_db()
    row = conn.execute('''
        SELECT id, otp_code, purpose, pending_payload, attempts, expires_at
        FROM otp_verifications
        WHERE LOWER(email) = ? AND purpose = ?
        ORDER BY id DESC LIMIT 1
    ''', (email, purpose)).fetchone()
    
    if not row:
        conn.close()
        return False, "No active verification code found for this email. Please request a new code.", None
        
    try:
        exp = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
        if exp < datetime.utcnow():
            conn.execute("DELETE FROM otp_verifications WHERE id = ?", (row['id'],))
            conn.commit()
            conn.close()
            return False, "The verification code has expired (valid for 5 minutes). Please request a new code.", None
    except Exception:
        pass
        
    if row['attempts'] >= 5:
        conn.execute("DELETE FROM otp_verifications WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        return False, "Too many incorrect attempts. For security, please request a new verification code.", None
        
    if row['otp_code'] != code:
        new_attempts = row['attempts'] + 1
        remaining = 5 - new_attempts
        conn.execute("UPDATE otp_verifications SET attempts = ? WHERE id = ?", (new_attempts, row['id']))
        conn.commit()
        conn.close()
        return False, f"Incorrect verification code. {remaining} attempt(s) remaining.", None
        
    # Valid code: delete it so it cannot be reused
    payload = json.loads(row['pending_payload']) if row['pending_payload'] else None
    conn.execute("DELETE FROM otp_verifications WHERE id = ?", (row['id'],))
    conn.commit()
    conn.close()
    
    return True, "Verification successful.", payload

def log_user_action(user_id: int, action_type: str, title: str, impact_metric: float, unit: str, notes: str = ''):
    """Logs a personal environmental action completed by the user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_eco_actions (user_id, action_type, title, impact_metric, unit, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, action_type, title, impact_metric, unit, notes))
    conn.commit()
    aid = cursor.lastrowid
    conn.close()
    return aid

def get_user_eco_actions(user_id: int, limit: int = 10):
    """Gets the user's logged eco actions."""
    conn = get_db()
    rows = conn.execute('''
        SELECT * FROM user_eco_actions
        WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_dashboard_summary(user_id: int):
    """Aggregates all user eco statistics, calculations, pledges, and achievements."""
    user = get_user_by_id(user_id)
    if not user:
        return None
        
    conn = get_db()
    
    # 1. User calculations
    calcs = conn.execute('''
        SELECT calc_type, result_metric, created_at
        FROM calculations
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 5
    ''', (user_id,)).fetchall()
    
    latest_carbon = None
    latest_water = None
    for c in calcs:
        if c['calc_type'] == 'carbon' and latest_carbon is None:
            latest_carbon = c['result_metric']
        elif c['calc_type'] == 'water' and latest_water is None:
            latest_water = c['result_metric']
            
    # Default benchmark values if user hasn't run calculator yet
    if latest_carbon is None:
        latest_carbon = 4.2  # Tonnes CO2/yr benchmark
    if latest_water is None:
        latest_water = 145.0 # Liters/day benchmark
        
    # 2. User pledges
    user_pledges = conn.execute('''
        SELECT id, city, pledges_list, created_at
        FROM pledges
        WHERE user_id = ? OR LOWER(email) = LOWER(?)
        ORDER BY id DESC LIMIT 5
    ''', (user_id, user['email'])).fetchall()
    
    pledges_count = len(user_pledges)
    
    # 3. User eco actions
    actions = conn.execute('''
        SELECT id, action_type, title, impact_metric, unit, notes, logged_at
        FROM user_eco_actions
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 15
    ''', (user_id,)).fetchall()
    
    total_actions = len(actions)
    
    # Calculate CO2 saved metric across actions
    co2_saved_kg = sum(a['impact_metric'] for a in actions if 'kg' in a['unit'].lower() or a['action_type'] in ['transit', 'energy', 'diet'])
    trees_equivalent = round(co2_saved_kg / 21.77, 1) if co2_saved_kg > 0 else 1.0
    
    # Determine Guardian Level
    score = (total_actions * 20) + (pledges_count * 50) + (len(calcs) * 30)
    if score >= 300:
        level = "Level 4: Planet Protector 🌍"
        badge = "Grand Guardian"
    elif score >= 150:
        level = "Level 3: Eco Champion 🛡️"
        badge = "Champion"
    elif score >= 50:
        level = "Level 2: Climate Guardian 🌱"
        badge = "Guardian"
    else:
        level = "Level 1: Green Explorer 🌿"
        badge = "Explorer"
        
    organizer_events = []
    if user.get('role') in ['organizer', 'admin', 'superadmin']:
        organizer_events = [dict(r) for r in conn.execute('SELECT * FROM events ORDER BY event_date ASC').fetchall()]

    admin_overview = {}
    if user.get('role') in ['admin', 'superadmin']:
        admin_overview = {
            'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'total_feedbacks': conn.execute('SELECT COUNT(*) FROM feedback').fetchone()[0],
            'total_subscribers': conn.execute('SELECT COUNT(*) FROM subscribers').fetchone()[0]
        }

    conn.close()
    
    return {
        'user': user,
        'eco_level': level,
        'badge': badge,
        'score': max(25, score),
        'latest_carbon_tonnes': round(latest_carbon, 2),
        'latest_water_liters': round(latest_water, 1),
        'co2_saved_kg': round(co2_saved_kg, 1),
        'trees_equivalent': trees_equivalent,
        'actions_count': total_actions,
        'pledges_count': pledges_count,
        'recent_actions': [dict(a) for a in actions],
        'recent_pledges': [dict(p) for p in user_pledges],
        'organizer_events': organizer_events,
        'admin_overview': admin_overview
    }

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_FILE)

