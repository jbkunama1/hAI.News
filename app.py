import os, sqlite3, time, threading, secrets, socket, ipaddress, re, logging, calendar, html
from urllib.parse import urlparse, urljoin
import requests, feedparser
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO)
PASSWORD=os.environ.get('ADMIN_PASSWORD','')
SECRET=os.environ.get('SECRET_KEY','')
if len(PASSWORD)<6 or len(SECRET)<32:
    raise RuntimeError('ADMIN_PASSWORD >=6 und SECRET_KEY >=32 Zeichen erforderlich')
HASH=generate_password_hash(PASSWORD)
app=Flask(__name__,static_folder='static')
app.secret_key=SECRET
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict',SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE','false').lower()=='true',MAX_CONTENT_LENGTH=32768)
DB=os.environ.get('DB_PATH','/data/news.db')
os.makedirs(os.path.dirname(os.path.abspath(DB)),exist_ok=True)
def db():
    c=sqlite3.connect(DB,timeout=30); c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON'); return c
SEEDS=[('DER SPIEGEL','https://www.spiegel.de/schlagzeilen/index.rss','Nachrichten'),('ntv','https://www.n-tv.de/rss','Nachrichten'),('Financial Times','https://www.ft.com/world?format=rss','Wirtschaft'),('CNN (experimentell)','https://rss.cnn.com/rss/edition.rss','International'),('heise online','https://www.heise.de/rss/heise-atom.xml','Technologie'),('Tagesschau','https://www.tagesschau.de/xml/rss2/','Nachrichten'),('TechCrunch','https://techcrunch.com/feed/','Technologie'),('Ars Technica','https://feeds.arstechnica.com/arstechnica/index','Technologie')]
with db() as c:
    c.executescript('CREATE TABLE IF NOT EXISTS feeds(id INTEGER PRIMARY KEY,name TEXT NOT NULL,url TEXT UNIQUE NOT NULL,category TEXT NOT NULL,enabled INTEGER DEFAULT 1,last_attempt REAL,last_success REAL,error TEXT); CREATE TABLE IF NOT EXISTS articles(id INTEGER PRIMARY KEY,feed_id INTEGER REFERENCES feeds(id) ON DELETE CASCADE,title TEXT,url TEXT UNIQUE,summary TEXT,published REAL); CREATE INDEX IF NOT EXISTS articles_date ON articles(published DESC); CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);')
    if not c.execute("SELECT 1 FROM settings WHERE key='seeded'").fetchone():
        c.executemany('INSERT OR IGNORE INTO feeds(name,url,category) VALUES(?,?,?)',SEEDS)
        c.execute("INSERT INTO settings VALUES('seeded','1')")
    c.execute("INSERT OR IGNORE INTO settings VALUES('interval','15')")

def public_url(url):
    p=urlparse(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.port not in (None,80,443):
        raise ValueError('Nur öffentliche HTTP(S)-URLs auf Standardports erlaubt')
    addresses=socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Private/interne Ziele sind gesperrt')
    return url

def download(url):
    for _ in range(5):
        public_url(url)
        with requests.get(url,timeout=(5,20),stream=True,allow_redirects=False,headers={'User-Agent':'hAI.News/0.1 RSS reader'}) as r:
            if r.is_redirect:
                url=urljoin(url,r.headers['Location']); continue
            r.raise_for_status(); chunks=[]; size=0
            for chunk in r.iter_content(65536):
                size+=len(chunk)
                if size>4*1024*1024: raise ValueError('Feed größer als 4 MiB')
                chunks.append(chunk)
            return b''.join(chunks)
    raise ValueError('Zu viele Weiterleitungen')

def text(value):
    return html.unescape(re.sub('<[^>]+>',' ',str(value or '')))[:1500].strip()
def article_url(value):
    p=urlparse(value)
    return value if p.scheme in ('http','https') and p.hostname and not p.username else None
lock=threading.Lock(); wake=threading.Event()
def refresh():
    if not lock.acquire(False): return
    try:
        with db() as c: feeds=c.execute('SELECT * FROM feeds WHERE enabled=1').fetchall()
        for f in feeds:
            now=time.time()
            try:
                parsed=feedparser.parse(download(f['url']))
                if not parsed.entries: raise ValueError('Keine Einträge – Feed leer, ungültig oder eingestellt')
                with db() as c:
                    for e in parsed.entries[:100]:
                        url=article_url(e.get('link',''))
                        if not url: continue
                        stamp=e.get('published_parsed') or e.get('updated_parsed')
                        published=min(calendar.timegm(stamp),now) if stamp else now
                        c.execute('INSERT OR IGNORE INTO articles(feed_id,title,url,summary,published) VALUES(?,?,?,?,?)',(f['id'],text(e.get('title','Ohne Titel')),url,text(e.get('summary','')),published))
                    c.execute('UPDATE feeds SET last_attempt=?,last_success=?,error=NULL WHERE id=?',(now,now,f['id']))
            except Exception as exc:
                logging.warning('Feed %s: %s',f['name'],exc)
                with db() as c: c.execute('UPDATE feeds SET last_attempt=?,error=? WHERE id=?',(now,str(exc)[:250],f['id']))
        with db() as c: c.execute('DELETE FROM articles WHERE published < ?',(time.time()-30*86400,))
    finally: lock.release()
def worker():
    while True:
        try: refresh()
        except Exception: logging.exception('Abruf fehlgeschlagen')
        with db() as c: minutes=int(c.execute("SELECT value FROM settings WHERE key='interval'").fetchone()[0])
        wake.wait(minutes*60); wake.clear()

attempts={}
@app.before_request
def guard():
    if request.path.startswith('/api/admin'):
        if not session.get('admin'): return jsonify(error='Anmeldung erforderlich'),401
        if request.method!='GET' and not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','!')): return jsonify(error='Ungültiges CSRF-Token'),403
@app.after_request
def headers(r):
    r.headers['X-Content-Type-Options']='nosniff'; r.headers['Referrer-Policy']='no-referrer'
    r.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if request.path.startswith('/api/'): r.headers['Cache-Control']='no-store'
    return r
@app.errorhandler(ValueError)
def invalid(e): return jsonify(error=str(e)),400
@app.get('/')
def index(): return send_from_directory('static','index.html')
@app.get('/health')
def health():
    with db() as c: c.execute('SELECT 1')
    return jsonify(status='ok',refreshing=lock.locked())
@app.get('/api/session')
def who():
    session.setdefault('csrf',secrets.token_hex(32))
    return jsonify(admin=bool(session.get('admin')),csrf=session['csrf'])
@app.post('/api/login')
def login():
    if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','!')): return jsonify(error='Seite neu laden'),403
    key=request.remote_addr; now=time.time()
    attempts[key]=[t for t in attempts.get(key,[]) if t>now-900]
    if len(attempts[key])>=8: return jsonify(error='Zu viele Versuche. 15 Minuten warten.'),429
    attempts[key].append(now)
    if not check_password_hash(HASH,str((request.json or {}).get('password',''))): return jsonify(error='Passwort falsch'),401
    attempts.pop(key,None); session.clear(); session.update(admin=True,csrf=secrets.token_hex(32))
    return jsonify(admin=True,csrf=session['csrf'])
@app.post('/api/admin/logout')
def logout(): session.clear(); return jsonify(ok=True)
@app.get('/api/news')
def news():
    q=request.args.get('q','')[:200]; category=request.args.get('category',''); source=request.args.get('source','')
    page=max(0,min(int(request.args.get('page',0)),10000)); where=['f.enabled=1']; params=[]
    if q: where.append('(a.title LIKE ? OR a.summary LIKE ?)'); params += ['%'+q+'%']*2
    if category: where.append('f.category=?'); params.append(category)
    if source: where.append('f.id=?'); params.append(source)
    with db() as c:
        rows=c.execute('SELECT a.*,f.name AS source,f.category FROM articles a JOIN feeds f ON a.feed_id=f.id WHERE '+' AND '.join(where)+' ORDER BY a.published DESC LIMIT 31 OFFSET ?',params+[page*30]).fetchall()
        feeds=c.execute('SELECT id,name,category,last_success,error FROM feeds WHERE enabled=1').fetchall()
        interval=int(c.execute("SELECT value FROM settings WHERE key='interval'").fetchone()[0])
    return jsonify(articles=[dict(x) for x in rows[:30]],more=len(rows)>30,feeds=[dict(x) for x in feeds],interval=interval,refreshing=lock.locked())
@app.get('/api/admin/feeds')
def feeds():
    with db() as c: return jsonify([dict(x) for x in c.execute('SELECT * FROM feeds')])
@app.post('/api/admin/feeds')
def add_feed():
    d=request.json or {}; url=public_url(str(d.get('url','')).strip()); name=text(d.get('name',''))[:100]; cat=text(d.get('category','Nachrichten'))[:50]
    if not name or not cat: raise ValueError('Name und Kategorie erforderlich')
    try:
        with db() as c: c.execute('INSERT INTO feeds(name,url,category) VALUES(?,?,?)',(name,url,cat))
    except sqlite3.IntegrityError: raise ValueError('Feed bereits vorhanden')
    wake.set(); return jsonify(ok=True)
@app.route('/api/admin/feeds/<int:fid>',methods=['PATCH','DELETE'])
def change_feed(fid):
    with db() as c:
        if request.method=='DELETE': c.execute('DELETE FROM feeds WHERE id=?',(fid,))
        else: c.execute('UPDATE feeds SET enabled=? WHERE id=?',(int(bool((request.json or {}).get('enabled'))),fid))
    return jsonify(ok=True)
@app.post('/api/admin/settings')
def settings():
    minutes=int((request.json or {}).get('interval',15))
    if not 5<=minutes<=1440: raise ValueError('Intervall: 5 bis 1440 Minuten')
    with db() as c: c.execute("UPDATE settings SET value=? WHERE key='interval'",(str(minutes),))
    wake.set(); return jsonify(ok=True)
@app.post('/api/admin/refresh')
def manual(): wake.set(); return jsonify(ok=True)
threading.Thread(target=worker,daemon=True).start()
