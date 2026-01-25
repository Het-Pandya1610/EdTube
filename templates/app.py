import os
from urllib.parse import urlparse
from flask import Flask, redirect, url_for, session, render_template, request, flash # type:ignore
from authlib.integrations.flask_client import OAuth # type:ignore
from dotenv import load_dotenv # type:ignore
import pymysql # type:ignore

load_dotenv()  # loads .env

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET") or "dev_secret_change_me"

# --- OAuth client setup ---
oauth = OAuth(app)

# Google registration
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Facebook registration
oauth.register(
    name='facebook',
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v12.0/',
    client_kwargs={'scope': 'email'},
)

# --- Database helper (pymysql) ---
def get_db_connection():
    # very simple connection helper; replace with your connection pooling in production
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set in .env")
    # parse mysql+pymysql://user:pass@host/dbname
    # you can use SQLAlchemy instead for nicer ORM
    parsed = urlparse(url)
    db = pymysql.connect(
        host=parsed.hostname or "localhost",
        user=parsed.username,
        password=parsed.password or "",
        db=parsed.path.lstrip("/"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return db

def find_or_create_user(profile, provider):
    """
    profile: dict containing at least 'email' and 'sub'/'id' and 'name' optionally 'picture'
    provider: 'google' or 'facebook'
    """
    email = profile.get('email')
    provider_id = profile.get('sub') or profile.get('id')  # google uses 'sub', facebook uses 'id'
    name = profile.get('name') or profile.get('given_name') or ''
    avatar = profile.get('picture') or profile.get('picture', {}).get('data', {}).get('url')

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # try find by provider_id first
            cur.execute("SELECT * FROM users WHERE provider = %s AND provider_id = %s", (provider, provider_id))
            user = cur.fetchone()
            if user:
                return user

            # fallback: find by email (if exists, link the provider)
            if email:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                if user:
                    # update to add provider info if missing
                    cur.execute("UPDATE users SET provider=%s, provider_id=%s, avatar=%s WHERE id=%s",
                                (provider, provider_id, avatar, user['id']))
                    conn.commit()
                    cur.execute("SELECT * FROM users WHERE id=%s", (user['id'],))
                    return cur.fetchone()

            # create new user
            cur.execute(
                "INSERT INTO users (fullname, email, provider, provider_id, avatar) VALUES (%s,%s,%s,%s,%s)",
                (name, email, provider, provider_id, avatar)
            )
            conn.commit()
            user_id = cur.lastrowid
            cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()

# --- Routes ---
@app.route("/")
def home():
    user = session.get("user")
    return render_template("EdTube.html", user=user)

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login/<provider>")
def oauth_login(provider):
    if provider not in ("google", "facebook"):
        return "Unsupported provider", 400
    redirect_uri = url_for("auth_callback", provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)

@app.route("/auth/callback/<provider>")
def auth_callback(provider):
    if provider not in ("google", "facebook"):
        return "Unsupported provider", 400

    client = oauth.create_client(provider)
    token = client.authorize_access_token()

    # fetch user info
    if provider == "google":
        # OIDC userinfo
        userinfo = client.parse_id_token(token) if token.get("id_token") else client.get("userinfo").json()
    else:
        # facebook: request fields explicitly
        userinfo = client.get("me?fields=id,name,email,picture{url}").json()

    # Normalize fields
    if provider == "facebook":
        profile = {
            "id": userinfo.get("id"),
            "name": userinfo.get("name"),
            "email": userinfo.get("email"),
            "picture": userinfo.get("picture", {}).get("data", {}).get("url")
        }
    else:
        profile = userinfo  # google returns 'sub', 'email', 'name', 'picture'

    # ensure we have email (sometimes facebook doesn't return it if user declined)
    if not profile.get("email"):
        flash("Email permission is required. Please allow email access and try again.", "error")
        return redirect(url_for("login_page"))

    # find or create user, store in session
    user = find_or_create_user(profile, provider)
    session["user"] = {
        "id": user["id"],
        "fullname": user["fullname"],
        "email": user["email"],
        "avatar": user.get("avatar"),
        "provider": user.get("provider")
    }

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# Run
if __name__ == "__main__":
    app.run(debug=True)
