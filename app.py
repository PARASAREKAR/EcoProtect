import os, sys, json, subprocess, re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, session, make_response, redirect, url_for
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_url_path='/static'
)
app.secret_key = 'ecoplanet_secret_key_environment_protection_website_2026'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

database.init_db()

# ── USER CONTEXT PROCESSOR & REMEMBER ME SESSION RESTORATION ───────────────
@app.before_request
def check_remember_token():
    if not session.get('user_id'):
        rem_tok = request.cookies.get('eco_remember_token')
        if rem_tok:
            user = database.verify_user_session(rem_tok)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']

@app.context_processor
def inject_user():
    user = None
    if session.get('user_id'):
        user = database.get_user_by_id(session['user_id'])
    return dict(current_user=user)

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CPP_EXE     = os.path.join(BASE_DIR, 'eco_engine.exe')

# ── Python fallback scientific engine ──────────────────────────────────────
def python_calculate_carbon(d):
    try:
        elec   = float(d.get('electricity_kwh', 250))
        gas    = float(d.get('gas_therms', 20))
        car    = float(d.get('car_km', 150))
        vtype  = d.get('vehicle_type','petrol').lower()
        transit= float(d.get('transit_km', 50))
        fs     = float(d.get('flights_short', 1))
        fl     = float(d.get('flights_long', 0))
        diet   = d.get('diet_type','average').lower()
        waste  = float(d.get('waste_bags', 2))
        recycle= min(0.9, max(0.0, float(d.get('recycling_rate', 0.3))))
        mem    = max(1, int(d.get('household_members', 1)))

        home_kg  = ((elec*12*0.475)+(gas*12*5.3))/mem
        cfactor  = 0.192 if vtype=='petrol' else (0.171 if vtype=='diesel' else 0.053)
        trans_kg = (car*52*cfactor)+(transit*52*0.089)
        avi_kg   = (fs*800*0.254)+(fl*4500*0.195)
        diet_map = {'meat_heavy':3300,'average':2500,'pescatarian':1900,'vegetarian':1500,'vegan':1050}
        diet_kg  = diet_map.get(diet, 2500)
        waste_kg = ((waste*10*52)/mem)*(1-recycle)*0.58

        total_kg     = home_kg+trans_kg+avi_kg+diet_kg+waste_kg
        total_tonnes = round(total_kg/1000, 2)
        trees        = int(round(total_kg/21.77))
        g_pct        = round(((total_tonnes-4.5)/4.5)*100,1)
        p_pct        = round(((total_tonnes-2.0)/2.0)*100,1)

        if   total_tonnes<=2.0: rating='A+ (Climate Hero)'
        elif total_tonnes<=3.5: rating='A (Eco Conscious)'
        elif total_tonnes<=5.5: rating='B (Moderate Impact)'
        elif total_tonnes<=8.5: rating='C (High Footprint)'
        else:                   rating='D (Urgent Action Required)'

        recs=[]
        if trans_kg>2000: recs.append("Shift commutes to cycling or public transit — saves 800+ kg CO₂.")
        if avi_kg>1000:   recs.append("Replace short flights with rail where possible.")
        if diet in ['meat_heavy','average']: recs.append("Plant-rich meals 3×/week can cut food emissions by 500 kg/yr.")
        if home_kg>1500:  recs.append("Switch to LED lighting and optimise your thermostat by 1-2°.")
        if recycle<0.5:   recs.append("Separate organics and recyclables to divert landfill methane.")
        if not recs: recs.append("Outstanding! Share your habits to amplify community impact.")

        return dict(status='success', engine='Python Embedded EcoEngine',
                    home_energy_kg=round(home_kg,1), transport_kg=round(trans_kg,1),
                    aviation_kg=round(avi_kg,1), diet_kg=round(diet_kg,1), waste_kg=round(waste_kg,1),
                    total_tonnes=total_tonnes, per_capita_tonnes=total_tonnes,
                    trees_needed=trees, global_comparison_pct=g_pct,
                    paris_target_comparison_pct=p_pct, eco_rating=rating, recommendations=recs)
    except Exception as e:
        return dict(status='error', message=str(e))

def python_calculate_water(d):
    try:
        shower  = float(d.get('shower_minutes',8))
        flushes = float(d.get('toilet_flushes',5))
        laundry = float(d.get('laundry_loads',3))
        dishes  = float(d.get('dish_loads',5))
        garden  = float(d.get('garden_mins',0))
        lf      = str(d.get('low_flow','false')).lower() in ['true','1','yes']
        size    = max(1,int(d.get('household_size',1)))

        slpm = 6.5 if lf else 12.0; fvol = 4.5 if lf else 9.0
        lcyc = 50  if lf else 90
        daily= (shower*slpm + flushes*fvol + (laundry*lcyc)/7 + (dishes*15)/7)*size + (garden*18)/7
        dpc  = round(daily/size,1)
        arm3 = round((daily*365)/1000,1)
        bpct = round(((dpc-140)/140)*100,1)
        tier = "Water Guardian ✅" if dpc<=120 else ("Moderate Saver" if dpc<=180 else "High Water Footprint")
        acts=[]
        if not lf: acts.append("Low-flow fixtures save 15,000 L/person/year.")
        if shower>7: acts.append("5-min showers save 35 L/day.")
        if garden>30: acts.append("Drip irrigation cuts garden evaporation by 40%.")
        if not acts: acts.append("Excellent! Consider a rainwater harvesting barrel.")
        return dict(status='success', engine='Python Embedded EcoEngine',
                    daily_liters_total=round(daily,1), daily_liters_per_capita=dpc,
                    annual_cubic_meters=arm3, global_benchmark_pct=bpct,
                    conservation_tier=tier, recommendations=acts)
    except Exception as e:
        return dict(status='error', message=str(e))

def run_calculation(data):
    if os.path.exists(CPP_EXE):
        try:
            proc = subprocess.run([CPP_EXE,'--json',json.dumps(data)],
                                  capture_output=True, text=True, timeout=5)
            if proc.returncode==0 and proc.stdout.strip():
                return json.loads(proc.stdout)
        except: pass
    return python_calculate_water(data) if data.get('type')=='water' else python_calculate_carbon(data)

# ── FRONT-END PAGE ROUTES ──────────────────────────────────────────────────
@app.route('/')
def home():       return render_template('index.html')

@app.route('/about')
def about():      return render_template('about.html')

@app.route('/problems')
def problems():   return render_template('problems.html')

@app.route('/climate')
def climate():    return render_template('climate.html')

@app.route('/biodiversity')
def biodiversity(): return render_template('biodiversity.html')

@app.route('/solutions')
def solutions():  return render_template('solutions.html')

@app.route('/forests')
def forests():    return render_template('forests.html')

@app.route('/water-conservation')
def water_con():  return render_template('water.html')

@app.route('/waste-management')
def waste_mgmt(): return render_template('waste.html')

@app.route('/renewable-energy')
def renewables(): return render_template('energy.html')

@app.route('/lifestyle')
def lifestyle():  return render_template('lifestyle.html')

@app.route('/calculator')
def calculator(): return render_template('calculator.html')

@app.route('/events')
def events_page():return render_template('events.html')

@app.route('/news')
def news_page():  return render_template('news.html')

@app.route('/pledge')
def pledge():     return render_template('pledge.html')

@app.route('/contact')
def contact():    return render_template('contact.html')

@app.route('/admin')
def admin_page(): return render_template('admin.html')

# ── Globe Hazards Master Dataset (4,800+ Incidents 1995-2026) ─────────────
MASTER_HAZARDS_PATH = os.path.join(BASE_DIR, 'static', 'data', 'hazards_master.json')
try:
    if os.path.exists(MASTER_HAZARDS_PATH):
        with open(MASTER_HAZARDS_PATH, 'r', encoding='utf-8') as f:
            GLOBAL_HAZARDS = json.load(f)
    else:
        from hazards_data import GLOBAL_HAZARDS
except Exception as e:
    print(f"Error loading master hazards: {e}")
    from hazards_data import GLOBAL_HAZARDS

HAZARDS_BY_ID = {h['id']: h for h in GLOBAL_HAZARDS}

@app.route('/globe')
def globe_page():
    return render_template('globe.html', total_hazards_count=len(GLOBAL_HAZARDS))

@app.route('/api/hazard/<int:hid>')
def api_hazard_detail(hid):
    h = HAZARDS_BY_ID.get(hid)
    if h:
        return jsonify(h)
    return jsonify({'status': 'error', 'message': 'Hazard not found'}), 404

@app.route('/login')
def login_page():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('auth.html', active_tab='login')

@app.route('/signup')
def signup_page():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('auth.html', active_tab='signup')

@app.route('/logout')
def logout():
    rem_tok = request.cookies.get('eco_remember_token')
    if rem_tok:
        database.delete_user_session(rem_tok)
    session.clear()
    resp = make_response(redirect('/login?logout=1'))
    resp.delete_cookie('eco_remember_token')
    return resp

@app.route('/dashboard')
def dashboard_page():
    if not session.get('user_id'):
        return redirect('/login?next=/dashboard&auth_required=1')
    user = database.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login?next=/dashboard&auth_required=1')
    return render_template('dashboard.html', user=user)

@app.route('/terms')
def terms_page():
    return render_template('terms.html')

@app.route('/api/hazards')
def api_hazards():
    year = request.args.get('year')
    country = request.args.get('country')
    category = request.args.get('category')
    search = request.args.get('search')
    
    results = GLOBAL_HAZARDS
    if year and year != 'all':
        try:
            y = int(year)
            results = [h for h in results if h.get('year') == y]
        except ValueError:
            pass
    if country and country.lower() != 'all':
        results = [h for h in results if h.get('country', '').lower() == country.lower()]
    if category and category.lower() != 'all':
        results = [h for h in results if h.get('category', '').lower() == category.lower()]
    if search:
        s = search.lower()
        results = [h for h in results if s in h.get('name', '').lower() or s in h.get('country', '').lower() or s in h.get('description', '').lower()]
        
    return jsonify(results)

# ── REST API (unchanged) ───────────────────────────────────────────────────
@app.route('/api/stats')
def api_stats():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM stats').fetchall()
    conn.close()
    return jsonify({r['key']:dict(r) for r in rows})

@app.route('/api/articles', methods=['GET','POST'])
def api_articles():
    conn = database.get_db()
    if request.method=='POST':
        d=request.json or {}
        title=d.get('title','').strip(); content=d.get('content','').strip()
        if not title or not content:
            conn.close(); return jsonify({'status':'error','message':'Title and content required'}),400
        cur=conn.cursor()
        cur.execute('INSERT INTO articles (title,category,summary,content,author,read_time,published_date) VALUES (?,?,?,?,?,?,?)',
            (title,d.get('category','General'),d.get('summary',''),content,
             d.get('author','EcoProtect'),d.get('read_time','4 min read'),datetime.now().strftime('%Y-%m-%d')))
        conn.commit(); nid=cur.lastrowid; conn.close()
        return jsonify({'status':'success','id':nid,'message':'Article published!'})
    cat=request.args.get('category'); srch=request.args.get('search')
    q='SELECT * FROM articles WHERE 1=1'; p=[]
    if cat and cat.lower()!='all': q+=' AND LOWER(category)=LOWER(?)'; p.append(cat)
    if srch:
        q+=' AND (title LIKE ? OR summary LIKE ? OR content LIKE ?)'; t=f'%{srch}%'; p+=[t,t,t]
    rows=conn.execute(q+' ORDER BY id DESC',p).fetchall(); conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/articles/<int:aid>', methods=['GET','DELETE'])
def api_article(aid):
    conn=database.get_db()
    if request.method=='DELETE':
        conn.execute('DELETE FROM articles WHERE id=?',(aid,)); conn.commit(); conn.close()
        return jsonify({'status':'success'})
    row=conn.execute('SELECT * FROM articles WHERE id=?',(aid,)).fetchone(); conn.close()
    return jsonify(dict(row)) if row else (jsonify({'status':'error'}),404)

@app.route('/api/events', methods=['GET','POST'])
def api_events():
    conn=database.get_db()
    if request.method=='POST':
        d=request.json or {}
        if not d.get('title') or not d.get('event_date') or not d.get('location'):
            conn.close(); return jsonify({'status':'error','message':'Title, date, location required'}),400
        cur=conn.cursor()
        cur.execute('INSERT INTO events (title,category,event_date,location,description,organizer,capacity) VALUES (?,?,?,?,?,?,?)',
            (d['title'],d.get('category','Campaign'),d['event_date'],d['location'],
             d.get('description',''),d.get('organizer','EcoProtect'),int(d.get('capacity',100))))
        conn.commit(); nid=cur.lastrowid; conn.close()
        return jsonify({'status':'success','id':nid,'message':'Event created!'})
    cat=request.args.get('category')
    q='SELECT * FROM events WHERE 1=1'; p=[]
    if cat and cat.lower()!='all': q+=' AND LOWER(category) LIKE LOWER(?)'; p.append(f'%{cat}%')
    rows=conn.execute(q+' ORDER BY event_date ASC',p).fetchall(); conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/events/<int:eid>/register', methods=['POST'])
def api_event_register(eid):
    d=request.json or {}; name=d.get('name','').strip(); email=d.get('email','').strip()
    if not name or not email: return jsonify({'status':'error','message':'Name and Email required'}),400
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',email):
        return jsonify({'status':'error','message':'Valid email required'}),400
    tickets=max(1,int(d.get('tickets',1)))
    conn=database.get_db()
    ev=conn.execute('SELECT * FROM events WHERE id=?',(eid,)).fetchone()
    if not ev: conn.close(); return jsonify({'status':'error','message':'Event not found'}),404
    if ev['registered_count']+tickets>ev['capacity']:
        conn.close(); return jsonify({'status':'error','message':'Not enough seats remaining'}),400
    cur=conn.cursor()
    cur.execute('INSERT INTO event_registrations (event_id,name,email,phone,tickets) VALUES (?,?,?,?,?)',
        (eid,name,email,d.get('phone',''),tickets))
    conn.execute('UPDATE events SET registered_count=registered_count+? WHERE id=?',(tickets,eid))
    conn.commit(); rid=cur.lastrowid; conn.close()
    return jsonify({'status':'success','ticket_code':f'ECO-{eid:03d}-{rid:04d}',
                    'event_title':ev['title'],'message':f'Registered! Code: ECO-{eid:03d}-{rid:04d}'})

@app.route('/api/events/<int:eid>', methods=['DELETE'])
def api_del_event(eid):
    conn=database.get_db(); conn.execute('DELETE FROM events WHERE id=?',(eid,)); conn.commit(); conn.close()
    return jsonify({'status':'success'})

@app.route('/api/feedback', methods=['GET','POST'])
def api_feedback():
    conn=database.get_db()
    if request.method=='POST':
        d=request.json or {}
        name=d.get('name','').strip(); email=d.get('email','').strip()
        subject=d.get('subject','').strip(); message=d.get('message','').strip()
        if not name or not email or not subject or not message:
            conn.close(); return jsonify({'status':'error','message':'All fields required'}),400
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',email):
            conn.close(); return jsonify({'status':'error','message':'Valid email required'}),400
        conn.execute('INSERT INTO feedback (name,email,subject,category,message) VALUES (?,?,?,?,?)',
            (name,email,subject,d.get('category','general'),message))
        conn.commit(); conn.close()
        return jsonify({'status':'success','message':'Thank you! Feedback received.'})
    rows=conn.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall(); conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/feedback/<int:fid>/status', methods=['PATCH'])
def api_feedback_status(fid):
    d=request.json or {}
    conn=database.get_db()
    conn.execute('UPDATE feedback SET status=? WHERE id=?',(d.get('status','Reviewed'),fid))
    conn.commit(); conn.close()
    return jsonify({'status':'success'})

@app.route('/api/pledges', methods=['GET','POST'])
def api_pledges():
    conn=database.get_db()
    if request.method=='POST':
        d=request.json or {}; name=d.get('name','').strip(); email=d.get('email','').strip()
        if not name or not email: conn.close(); return jsonify({'status':'error','message':'Name and Email required'}),400
        pl=d.get('pledges',[]); pl_str=','.join(pl) if isinstance(pl,list) else str(pl)
        uid = session.get('user_id')
        cur=conn.cursor()
        cur.execute('INSERT INTO pledges (name,email,city,pledges_list,user_id) VALUES (?,?,?,?,?)',
            (name,email,d.get('city','Global'),pl_str,uid))
        conn.execute("UPDATE stats SET value=CAST(CAST(value AS INTEGER)+1 AS TEXT) WHERE key='pledges_count'")
        conn.commit(); bid=f'ECO-PLEDGE-{cur.lastrowid:05d}'; conn.close()
        return jsonify({'status':'success','badge_id':bid,'name':name,
                        'pledge_count':len(pl) if isinstance(pl,list) else 1,
                        'message':'Pledge signed! Your certificate is ready.'})
    total=conn.execute('SELECT COUNT(*) FROM pledges').fetchone()[0]
    recent=conn.execute('SELECT name,city,created_at FROM pledges ORDER BY id DESC LIMIT 6').fetchall()
    conn.close()
    return jsonify({'total_pledges':total+12480,'recent':[dict(r) for r in recent]})

@app.route('/api/newsletter', methods=['POST'])
def api_newsletter():
    d=request.json or {}; email=d.get('email','').strip()
    if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',email):
        return jsonify({'status':'error','message':'Valid email required'}),400
    conn=database.get_db()
    try:
        conn.execute('INSERT INTO subscribers (email) VALUES (?)',(email,)); conn.commit(); conn.close()
        return jsonify({'status':'success','message':'Subscribed! Monthly digest incoming.'})
    except:
        conn.close(); return jsonify({'status':'info','message':'Already subscribed!'})

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    d=request.json or {}; result=run_calculation(d)
    try:
        conn=database.get_db(); val=result.get('total_tonnes',result.get('daily_liters_total',0.0))
        uid = session.get('user_id')
        conn.execute('INSERT INTO calculations (calc_type,result_metric,user_id) VALUES (?,?,?)',(d.get('type','carbon'),float(val),uid))
        conn.commit(); conn.close()
    except: pass
    return jsonify(result)

# ── USER AUTHENTICATION & REMEMBER ME ENDPOINTS ────────────────────────────
def mask_email(email: str) -> str:
    """Masks an email for secure OTP display, e.g. a***n@ecoprotect.org."""
    if not email or '@' not in email:
        return email
    parts = email.split('@', 1)
    name, domain = parts[0], parts[1]
    if len(name) <= 2:
        masked_name = name[0] + '*'
    else:
        masked_name = name[0] + ('*' * (len(name) - 2)) + name[-1]
    return f"{masked_name}@{domain}"

@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    d = request.json or {}
    username = d.get('username', '').strip()
    email = d.get('email', '').strip().lower()
    password = d.get('password', '').strip()
    full_name = d.get('full_name', '').strip()
    city = d.get('city', '').strip()
    focus_area = d.get('focus_area', 'General').strip()
    terms_accepted = 1 if d.get('terms_accepted') else 0
    remember_me = bool(d.get('remember_me', True))
    
    if not terms_accepted:
        return jsonify({'status': 'error', 'message': 'You must accept the Environmental Platform Terms & Conditions.'}), 400
        
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'status': 'error', 'message': 'Please provide a valid email address.'}), 400
        
    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters long.'}), 400

    role = d.get('role', 'participant').strip().lower()
    if role not in ['participant', 'organizer']:
        role = 'participant'
        
    # Check if username or email already exists
    conn = database.get_db()
    existing = conn.execute("SELECT id FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?", (username.lower(), email)).fetchone()
    conn.close()
    if existing:
        return jsonify({'status': 'error', 'message': 'An account with this username or email already exists.'}), 400
        
    # Store registration details as pending verification
    pending_payload = {
        'username': username,
        'email': email,
        'password': password,
        'full_name': full_name,
        'city': city,
        'focus_area': focus_area,
        'terms_accepted': terms_accepted,
        'role': role,
        'remember_me': remember_me
    }
    
    otp = database.generate_otp(email, purpose='register', pending_payload=pending_payload, expiry_minutes=5)
    print(f"\n[OTP SERVICE] [REGISTRATION] New OTP for {email}: {otp}\n")
    
    return jsonify({
        'status': 'otp_required',
        'purpose': 'register',
        'email': email,
        'masked_email': mask_email(email),
        'demo_otp': otp,
        'remember_me': remember_me,
        'message': f'A 6-digit verification code has been dispatched to {mask_email(email)}.'
    })

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    d = request.json or {}
    identifier = d.get('identifier', '').strip()
    password = d.get('password', '').strip()
    remember_me = bool(d.get('remember_me', True))
    
    if not identifier or not password:
        return jsonify({'status': 'error', 'message': 'Username/Email and Password are required.'}), 400
        
    user = database.authenticate_user(identifier, password)
    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid credentials. Please verify your username/email and password.'}), 401
        
    # Credentials are valid -> Generate 6-digit OTP for 2-Factor Authentication
    pending_payload = {
        'user_id': user['id'],
        'email': user['email'],
        'remember_me': remember_me
    }
    otp = database.generate_otp(user['email'], purpose='login', pending_payload=pending_payload, expiry_minutes=5)
    print(f"\n[OTP SERVICE] [LOGIN 2FA] OTP for {user['email']} ({user['username']}): {otp}\n")
    
    return jsonify({
        'status': 'otp_required',
        'purpose': 'login',
        'email': user['email'],
        'masked_email': mask_email(user['email']),
        'user_name': user['full_name'],
        'demo_otp': otp,
        'remember_me': remember_me,
        'message': f'Credentials verified! A 6-digit OTP code has been dispatched to {mask_email(user["email"])}.'
    })

@app.route('/api/auth/verify-otp', methods=['POST'])
def api_auth_verify_otp():
    d = request.json or {}
    email = d.get('email', '').strip().lower()
    otp_code = d.get('otp_code', '').strip()
    purpose = d.get('purpose', 'login').strip().lower()
    remember_me = bool(d.get('remember_me', True))
    
    if not email or not otp_code:
        return jsonify({'status': 'error', 'message': 'Email address and 6-digit code are required.'}), 400
        
    ok, msg, payload = database.verify_otp(email, otp_code, purpose=purpose)
    if not ok:
        return jsonify({'status': 'error', 'message': msg}), 400
        
    if purpose == 'register':
        if not payload:
            return jsonify({'status': 'error', 'message': 'Registration session expired. Please submit registration again.'}), 400
        user_id, err = database.register_user(
            username=payload['username'],
            email=payload['email'],
            password=payload['password'],
            full_name=payload.get('full_name', ''),
            city=payload.get('city', ''),
            focus_area=payload.get('focus_area', 'General'),
            terms_accepted=payload.get('terms_accepted', 1),
            role=payload.get('role', 'participant')
        )
        if err:
            return jsonify({'status': 'error', 'message': err}), 400
        user = database.get_user_by_id(user_id)
        remember_me = payload.get('remember_me', True)
    else:
        user = database.get_user_by_email(email)
        if not user:
            return jsonify({'status': 'error', 'message': 'User profile not found.'}), 404
        if payload and 'remember_me' in payload:
            remember_me = payload['remember_me']
            
    # Session establishment & persistent cookie
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '')
    ua = request.headers.get('User-Agent', '')
    tok, exp = database.create_user_session(user['id'], remember_me=remember_me, ip_address=ip, user_agent=ua)
    
    resp = jsonify({
        'status': 'success',
        'message': f'Authentication complete! Welcome back, {user["full_name"]}.',
        'user': user,
        'redirect_url': '/dashboard'
    })
    max_age = 30 * 86400 if remember_me else 86400
    resp.set_cookie('eco_remember_token', tok, max_age=max_age, httponly=True, samesite='Lax')
    return resp

@app.route('/api/auth/resend-otp', methods=['POST'])
def api_auth_resend_otp():
    d = request.json or {}
    email = d.get('email', '').strip().lower()
    purpose = d.get('purpose', 'login').strip().lower()
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Email address required.'}), 400
        
    conn = database.get_db()
    existing = conn.execute(
        "SELECT pending_payload FROM otp_verifications WHERE LOWER(email) = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
        (email, purpose)
    ).fetchone()
    conn.close()
    
    pending_payload = json.loads(existing['pending_payload']) if (existing and existing['pending_payload']) else None
    
    if purpose == 'login':
        user = database.get_user_by_email(email)
        if not user:
            return jsonify({'status': 'error', 'message': 'No registered account found with this email.'}), 404
            
    otp = database.generate_otp(email, purpose=purpose, pending_payload=pending_payload, expiry_minutes=5)
    print(f"\n[OTP SERVICE] [RESEND] 6-digit OTP for {email} ({purpose}): {otp}\n")
    
    return jsonify({
        'status': 'success',
        'message': f'A fresh 6-digit verification code has been dispatched to {mask_email(email)}.',
        'masked_email': mask_email(email),
        'demo_otp': otp
    })

@app.route('/api/auth/me')
def api_auth_me():
    if not session.get('user_id'):
        return jsonify({'status': 'unauthenticated', 'user': None})
    user = database.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'status': 'unauthenticated', 'user': None})
    summary = database.get_user_dashboard_summary(user['id'])
    return jsonify({'status': 'authenticated', 'user': user, 'summary': summary})

@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    rem_tok = request.cookies.get('eco_remember_token')
    if rem_tok:
        database.delete_user_session(rem_tok)
    session.clear()
    resp = jsonify({'status': 'success', 'message': 'Logged out successfully.'})
    resp.delete_cookie('eco_remember_token')
    return resp

# ── DASHBOARD & ENVIRONMENTAL CONTROL ENDPOINTS ────────────────────────────
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    user_id = session.get('user_id')
    user_summary = database.get_user_dashboard_summary(user_id) if user_id else None
    
    # Global Planetary Control Indicators
    conn = database.get_db()
    total_pledges = conn.execute('SELECT COUNT(*) FROM pledges').fetchone()[0] + 12480
    total_calcs = conn.execute('SELECT COUNT(*) FROM calculations').fetchone()[0]
    total_trees = 58240 + (total_calcs * 3)
    conn.close()
    
    planetary_indicators = {
        'atmospheric_co2_ppm': 422.5,
        'co2_growth_rate': '+2.4 ppm/yr',
        'global_temp_anomaly_c': 1.28,
        'global_forest_cover_pct': 31.2,
        'renewable_power_share_pct': 30.2,
        'clean_water_stress_people_b': 2.2,
        'total_community_pledges': total_pledges,
        'total_trees_planted': total_trees,
        'ozone_recovery_status': 'Healing (Polar closure projected 2045)',
        'global_aqi_composite': 68
    }
    
    return jsonify({
        'status': 'success',
        'user_summary': user_summary,
        'planetary_indicators': planetary_indicators
    })

@app.route('/api/dashboard/log-action', methods=['POST'])
def api_dashboard_log_action():
    if not session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'Please sign in to log environmental actions.'}), 401
    d = request.json or {}
    action_type = d.get('action_type', 'general')
    title = d.get('title', '').strip()
    impact_metric = float(d.get('impact_metric', 1.0))
    unit = d.get('unit', 'kg CO2')
    notes = d.get('notes', '').strip()
    
    if not title:
        return jsonify({'status': 'error', 'message': 'Action title is required.'}), 400
        
    aid = database.log_user_action(session['user_id'], action_type, title, impact_metric, unit, notes)
    summary = database.get_user_dashboard_summary(session['user_id'])
    return jsonify({'status': 'success', 'message': 'Action logged to your dashboard!', 'action_id': aid, 'summary': summary})

@app.route('/api/dashboard/simulate', methods=['POST'])
def api_dashboard_simulate():
    d = request.json or {}
    car_reduction_pct = float(d.get('car_reduction_pct', 0))
    solar_share_pct = float(d.get('solar_share_pct', 0))
    plant_diet_days = int(d.get('plant_diet_days', 0))
    waste_recycle_pct = float(d.get('waste_recycle_pct', 0))
    
    # Scientific mitigation formula
    car_savings_kg = (car_reduction_pct / 100.0) * 1800.0
    solar_savings_kg = (solar_share_pct / 100.0) * 1400.0
    diet_savings_kg = plant_diet_days * 52 * 2.8
    waste_savings_kg = (waste_recycle_pct / 100.0) * 220.0
    
    total_annual_co2_kg = car_savings_kg + solar_savings_kg + diet_savings_kg + waste_savings_kg
    trees_equivalent = round(total_annual_co2_kg / 21.77, 1)
    
    return jsonify({
        'status': 'success',
        'total_annual_co2_kg': round(total_annual_co2_kg, 1),
        'total_annual_co2_tonnes': round(total_annual_co2_kg / 1000.0, 2),
        'trees_equivalent': trees_equivalent,
        'breakdown': {
            'transit_kg': round(car_savings_kg, 1),
            'clean_energy_kg': round(solar_savings_kg, 1),
            'dietary_kg': round(diet_savings_kg, 1),
            'waste_kg': round(waste_savings_kg, 1)
        }
    })

@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    d=request.json or {}; u=d.get('username','').strip(); p=d.get('password','').strip()
    if not u or not p: return jsonify({'status':'error','message':'Credentials required'}),400
    ph=database.hash_password(p)
    conn=database.get_db()
    user=conn.execute('SELECT * FROM users WHERE username=? AND password_hash=?',(u,ph)).fetchone()
    conn.close()
    if user:
        session['user_id']=user['id']; session['username']=user['username']
        return jsonify({'status':'success','token':'eco_admin_tok','username':user['username'],'role':user['role']})
    return jsonify({'status':'error','message':'Invalid credentials'}),401

@app.route('/api/admin/overview')
def api_admin_overview():
    conn=database.get_db()
    data=dict(
        feedbacks_count=conn.execute('SELECT COUNT(*) FROM feedback').fetchone()[0],
        pending_feedbacks=conn.execute("SELECT COUNT(*) FROM feedback WHERE status='Pending'").fetchone()[0],
        events_count=conn.execute('SELECT COUNT(*) FROM events').fetchone()[0],
        registrations_count=conn.execute('SELECT COUNT(*) FROM event_registrations').fetchone()[0],
        articles_count=conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0],
        pledges_count=conn.execute('SELECT COUNT(*) FROM pledges').fetchone()[0]+12480,
        subscribers_count=conn.execute('SELECT COUNT(*) FROM subscribers').fetchone()[0],
        calculations_run=conn.execute('SELECT COUNT(*) FROM calculations').fetchone()[0],
        cpp_engine_active=os.path.exists(CPP_EXE),
        cpp_binary_path=CPP_EXE if os.path.exists(CPP_EXE) else 'Not compiled – using Python engine'
    )
    conn.close(); return jsonify(data)

if __name__=='__main__':
    port=int(os.environ.get('PORT',5000))
    print(f"\n{'='*60}\n  EcoProtect | http://127.0.0.1:{port}\n  Admin      | http://127.0.0.1:{port}/admin\n{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
