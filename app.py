import streamlit as st
import secrets
import hashlib
import hmac
import time
import os
import sqlite3

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CONFIGURATION
# =========================================================

DEMO_PIN = "123456"
HMAC_SECRET = b"secure-digilocker-academic-demo-secret"

# Separate application-wide secret ("pepper") for the pattern hash.
# Combined with a per-user random salt, so a full DB leak alone is
# not enough to crack stored pattern hashes without this value too.
PATTERN_PEPPER = b"secure-digilocker-pattern-pepper-change-me"
PBKDF2_ITERATIONS = 200_000
MIN_PATTERN_LENGTH = 4

MAX_ATTEMPTS = 3
OTP_VALID_SECONDS = 60

DB_PATH = os.path.join(os.path.dirname(__file__), "digilocker.db")


# =========================================================
# PERSISTENT STORAGE (SQLite)
#
# This is the key structural change: the enrolled pattern is no
# longer kept in st.session_state (which is per-tab, in-memory,
# and wiped on restart). It is hashed and written to a small local
# database keyed by mobile number, so it survives across sessions
# and new devices the way a real "step-up auth" factor needs to.
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patterns (
            user_id TEXT PRIMARY KEY,
            salt BLOB NOT NULL,
            pattern_hash BLOB NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    return conn


def hash_pattern(sequence, salt):
    """PBKDF2-HMAC-SHA256 over the ordered tap sequence, salted and peppered."""
    raw = "-".join(str(n) for n in sequence).encode() + PATTERN_PEPPER
    return hashlib.pbkdf2_hmac("sha256", raw, salt, PBKDF2_ITERATIONS)


def pattern_is_enrolled(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM patterns WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row is not None


def save_pattern(user_id, sequence):
    salt = os.urandom(16)
    digest = hash_pattern(sequence, salt)
    conn = get_connection()
    conn.execute(
        "REPLACE INTO patterns (user_id, salt, pattern_hash, created_at) VALUES (?, ?, ?, ?)",
        (user_id, salt, digest, time.time())
    )
    conn.commit()
    conn.close()


def verify_pattern_attempt(user_id, tapped_sequence):
    conn = get_connection()
    row = conn.execute(
        "SELECT salt, pattern_hash FROM patterns WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return False

    salt, stored_hash = row
    attempt_hash = hash_pattern(tapped_sequence, salt)

    return hmac.compare_digest(attempt_hash, stored_hash)


def delete_pattern(user_id):
    """Used only by the demo 'reset my enrollment' control."""
    conn = get_connection()
    conn.execute("DELETE FROM patterns WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# =========================================================
# DOCUMENT DATA
# =========================================================

DOCUMENTS = [
    {"name": "🪪 Aadhaar Card", "authority": "UIDAI", "status": "Verified", "date": "15 Jan 2025"},
    {"name": "🚗 Driving Licence", "authority": "Transport Department", "status": "Verified", "date": "20 Feb 2025"},
    {"name": "🗳️ Voter ID", "authority": "Election Commission", "status": "Verified", "date": "10 Mar 2025"},
    {"name": "🎓 Class 10 Certificate", "authority": "Education Board", "status": "Verified", "date": "05 Apr 2025"},
    {"name": "🎓 Class 12 Certificate", "authority": "Education Board", "status": "Verified", "date": "12 May 2025"},
    {"name": "🎓 Degree Certificate", "authority": "University", "status": "Verified", "date": "15 Jun 2025"},
    {"name": "📄 PAN Card", "authority": "Income Tax Department", "status": "Verified", "date": "18 Jul 2025"},
    {"name": "🏥 Health Certificate", "authority": "Health Department", "status": "Verified", "date": "22 Aug 2025"},
    {"name": "🏦 Income Certificate", "authority": "Revenue Department", "status": "Verified", "date": "30 Sep 2025"},
    {"name": "📑 Other Documents", "authority": "Various Authorities", "status": "Available", "date": "01 Oct 2025"}
]


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "mobile_number": "",
    "stage": "mobile",

    "pin_attempts": 0,
    "pin_verified": False,

    "otp_hash": "",
    "otp_created_at": 0.0,
    "otp_attempts": 0,
    "otp_used": False,
    "otp_verified": False,
    "demo_otp": "",

    "physical_grid": [],
    "entered_pattern": [],
    "pattern_attempts": 0,
    "pattern_verified": False,

    "login_status": False,

    "font_scale": 1.0,
    "demo_mode": True
}


for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SECURITY FUNCTIONS (PIN / OTP — unchanged from before)
# =========================================================

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def otp_digest(otp):
    return hmac.new(HMAC_SECRET, otp.encode(), hashlib.sha256).hexdigest()


def verify_otp(otp):
    if not st.session_state.otp_hash:
        return False
    return hmac.compare_digest(otp_digest(otp), st.session_state.otp_hash)


def generate_grid():
    """Shuffles where each number 1-9 appears on screen. The displayed
    value tapped is still the real secret — this only randomizes layout
    so a captured screen or shoulder-surf from one login doesn't help
    on the next one."""
    layout = list(range(1, 10))
    secrets.SystemRandom().shuffle(layout)
    return layout


# =========================================================
# AUTHENTICATION FUNCTIONS
# =========================================================

def create_new_otp():
    otp = generate_otp()

    st.session_state.demo_otp = otp
    st.session_state.otp_hash = otp_digest(otp)
    st.session_state.otp_created_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False

    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False

    st.session_state.stage = "otp"


def start_authentication(mobile):
    st.session_state.mobile_number = mobile

    st.session_state.pin_attempts = 0
    st.session_state.pin_verified = False

    st.session_state.otp_hash = ""
    st.session_state.otp_created_at = 0.0
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False
    st.session_state.demo_otp = ""

    st.session_state.physical_grid = []
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False

    st.session_state.login_status = False

    st.session_state.stage = "pin"


def restart_login():
    # Only session_state is wiped. The enrolled pattern stays in
    # SQLite — restarting a login attempt must not erase the secret.
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


def logout():
    restart_login()


def otp_remaining():
    if not st.session_state.otp_created_at:
        return 0
    elapsed = int(time.time() - st.session_state.otp_created_at)
    return max(0, OTP_VALID_SECONDS - elapsed)


# =========================================================
# CSS
# =========================================================

scale = st.session_state.font_scale

st.markdown(
    f"""
    <style>
    .stApp {{ background: #f5f1ff; font-size: {scale}em; }}
    .block-container {{ max-width: 900px; padding-top: 1.5rem; padding-bottom: 3rem; }}
    .gov-header {{
        background: #10246b; color: white; padding: 14px 18px; border-radius: 8px;
        font-weight: 700; margin-bottom: 20px; text-align: center;
    }}
    .brand {{ text-align: center; font-size: 30px; font-weight: 700; color: #4325a8; margin-top: 10px; }}
    .brand-sub {{ text-align: center; color: #666666; margin-bottom: 15px; }}
    .prototype {{
        display: inline-block; background: #eee8ff; color: #4325a8; padding: 5px 10px;
        border-radius: 20px; font-size: 12px; font-weight: 700; margin-top: 8px;
    }}
    .login-card {{
        background: white; border: 1px solid #ddd5ef; border-radius: 18px; padding: 28px;
        margin: 25px auto; box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    }}
    .login-title {{ font-size: 30px; font-weight: 700; text-align: center; color: #111111; }}
    .login-subtitle {{ text-align: center; color: #666666; margin-top: 5px; margin-bottom: 15px; }}
    .info-box {{ background: #e9efff; padding: 15px; border-radius: 10px; margin: 15px 0; }}
    .section-title {{ font-size: 28px; font-weight: 700; margin: 20px 0; }}
    .dashboard-banner {{
        background: linear-gradient(135deg, #5634dd, #7d5bea); color: white; padding: 25px;
        border-radius: 18px; margin-bottom: 22px;
    }}
    .dashboard-banner h1 {{ margin: 0; font-size: 30px; }}
    .footer {{ text-align: center; color: #666666; padding: 25px 10px; font-size: 13px; }}
    @media (max-width: 600px) {{
        .block-container {{ padding-left: 12px; padding-right: 12px; }}
        .gov-header {{ font-size: 13px; padding: 12px 8px; }}
        .brand {{ font-size: 24px; }}
        .login-card {{ padding: 20px 15px; margin: 15px 0; }}
        .login-title {{ font-size: 25px; }}
        .section-title {{ font-size: 23px; }}
        .dashboard-banner {{ padding: 20px; }}
        .dashboard-banner h1 {{ font-size: 24px; }}
        button {{ min-height: 48px !important; }}
        input {{ min-height: 48px !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown('<div class="gov-header">🇮🇳 Government of India | Secure Digital Services</div>', unsafe_allow_html=True)
st.markdown('<div class="brand">🔐 Secure DigiLocker</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;"><span class="prototype">ACADEMIC PROTOTYPE</span></div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Secure digital document access</div>', unsafe_allow_html=True)

with st.expander("♿ Accessibility"):
    st.write("Adjust text size:")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("A−", use_container_width=True):
            st.session_state.font_scale = max(0.8, st.session_state.font_scale - 0.1)
            st.rerun()
    with c2:
        if st.button("A", use_container_width=True):
            st.session_state.font_scale = 1.0
            st.rerun()
    with c3:
        if st.button("A+", use_container_width=True):
            st.session_state.font_scale = min(1.5, st.session_state.font_scale + 0.1)
            st.rerun()


# =========================================================
# MOBILE NUMBER
# =========================================================

if st.session_state.stage == "mobile":

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Login or Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Enter your mobile number to proceed</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    mobile = st.text_input("Mobile Number", placeholder="10-digit mobile number", max_chars=10)
    st.caption("🇮🇳 +91 India")

    if st.button("Continue", type="primary", use_container_width=True):
        cleaned = mobile.strip().replace(" ", "")

        if not cleaned.isdigit() or len(cleaned) != 10:
            st.error("Please enter a valid 10-digit mobile number.")
        elif cleaned[0] not in "6789":
            st.error("Please enter a valid Indian mobile number.")
        else:
            start_authentication(cleaned)
            st.rerun()

    st.caption("By continuing, I agree to the Terms of Service.")
    st.divider()

    if st.button("📱 Login using QR Code", use_container_width=True):
        st.info("QR login is simulated for this academic prototype.")

    st.info(
        "Academic Prototype: This application uses dummy data "
        "and does not connect to real DigiLocker services."
    )


# =========================================================
# SECURITY PIN
# =========================================================

elif st.session_state.stage == "pin":

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Enter Security PIN</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Enter your 6-digit Security PIN to continue</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("Demo Security PIN: 123456")

    pin = st.text_input("Security PIN", type="password", max_chars=6, placeholder="Enter 6-digit PIN")

    if st.button("Continue", type="primary", use_container_width=True):

        if not pin.isdigit() or len(pin) != 6:
            st.error("Please enter a valid 6-digit Security PIN.")
        elif hmac.compare_digest(hash_pin(pin), hash_pin(DEMO_PIN)):
            st.session_state.pin_verified = True
            create_new_otp()
            st.rerun()
        else:
            st.session_state.pin_attempts += 1
            remaining = MAX_ATTEMPTS - st.session_state.pin_attempts

            if remaining > 0:
                st.error("Incorrect Security PIN.")
                st.warning(f"Remaining attempts: {remaining}")
            else:
                st.error("Too many incorrect attempts. Please restart authentication.")
                st.session_state.stage = "locked"

    if st.button("← Back", use_container_width=True):
        st.session_state.stage = "mobile"
        st.rerun()

    if st.button("Forgot Security PIN?", use_container_width=True):
        st.info("Demo feature: In a real system, PIN recovery would use a secure account-recovery process.")

    st.caption(f"PIN attempts: {st.session_state.pin_attempts}/{MAX_ATTEMPTS}")


# =========================================================
# ACCOUNT LOCKED
# =========================================================

elif st.session_state.stage == "locked":

    st.error("Authentication has been temporarily stopped because too many incorrect Security PIN attempts were made.")
    st.warning("Please restart the authentication process.")

    if st.button("Restart Login", type="primary", use_container_width=True):
        restart_login()


# =========================================================
# OTP
# =========================================================

elif st.session_state.stage == "otp":

    if st_autorefresh is not None:
        st_autorefresh(interval=1000, key="otp_timer")

    remaining_seconds = otp_remaining()

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">OTP Verification</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Verify your registered mobile number</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("Demo OTP — In a real system this would be sent through SMS.")
    st.success(f"Demo OTP: {st.session_state.demo_otp}")
    st.metric("OTP Valid For", f"{remaining_seconds} seconds")

    if remaining_seconds <= 0:
        st.error("The OTP has expired.")
        if st.button("Resend OTP", type="primary", use_container_width=True):
            create_new_otp()
            st.rerun()
    else:
        otp_input = st.text_input("Enter 6-digit OTP", max_chars=6, placeholder="Enter OTP", type="password")

        if st.button("Verify OTP", type="primary", use_container_width=True):

            if st.session_state.otp_used:
                st.error("This OTP has already been used.")
            elif not otp_input.isdigit() or len(otp_input) != 6:
                st.error("Please enter a valid 6-digit OTP.")
            elif remaining_seconds <= 0:
                st.error("The OTP has expired. Please request a new OTP.")
            elif st.session_state.otp_attempts >= MAX_ATTEMPTS:
                st.error("Too many incorrect OTP attempts. Please request a new OTP.")
            elif verify_otp(otp_input):
                st.session_state.otp_used = True
                st.session_state.otp_verified = True

                st.session_state.entered_pattern = []
                st.session_state.pattern_attempts = 0

                # Route based on whether this mobile number already has a
                # pattern saved in the database, not in session state.
                if pattern_is_enrolled(st.session_state.mobile_number):
                    st.session_state.physical_grid = generate_grid()
                    st.session_state.stage = "pattern"
                else:
                    st.session_state.stage = "pattern_setup"

                st.rerun()
            else:
                st.session_state.otp_attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.otp_attempts

                if remaining > 0:
                    st.error("Incorrect OTP.")
                    st.warning(f"Remaining attempts: {remaining}")
                else:
                    st.error("Too many incorrect OTP attempts. Please request a new OTP.")

        if st.button("Resend OTP", use_container_width=True):
            create_new_otp()
            st.rerun()

    if st.button("← Back", use_container_width=True):
        st.session_state.stage = "pin"
        st.rerun()


# =========================================================
# PATTERN SETUP (first time only, saved to SQLite)
# =========================================================

elif st.session_state.stage == "pattern_setup":

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Create Your Security Pattern</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Choose a sequence you can remember — this becomes your permanent pattern</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "This pattern is hashed and stored for your account. It will never be "
        "shown back to you after you save it — only you will know it."
    )
    st.warning(
        f"Choose at least {MIN_PATTERN_LENGTH} numbers. Avoid simple runs like "
        "1-2-3-4 or a single repeated digit — treat it like a PIN, not a doodle."
    )

    st.subheader("Tap numbers in the order you want to memorize")

    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            number = row * 3 + col + 1
            with cols[col]:
                if number in st.session_state.entered_pattern:
                    position = st.session_state.entered_pattern.index(number) + 1
                    label = f"✓ {number}  ({position})"
                else:
                    label = str(number)

                if st.button(label, key=f"setup_{number}", use_container_width=True):
                    if number not in st.session_state.entered_pattern:
                        st.session_state.entered_pattern.append(number)
                        st.rerun()

    entered_text = " → ".join(str(n) for n in st.session_state.entered_pattern) or "—"
    st.write(f"**Pattern selected:** {entered_text}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear", use_container_width=True):
            st.session_state.entered_pattern = []
            st.rerun()
    with c2:
        if st.button("Save Pattern", type="primary", use_container_width=True):
            if len(st.session_state.entered_pattern) < MIN_PATTERN_LENGTH:
                st.error(f"Select at least {MIN_PATTERN_LENGTH} numbers.")
            else:
                save_pattern(st.session_state.mobile_number, st.session_state.entered_pattern)
                st.session_state.entered_pattern = []
                st.session_state.pattern_verified = True
                st.session_state.login_status = True
                st.session_state.stage = "dashboard"
                st.rerun()


# =========================================================
# PATTERN VERIFICATION (returning device, checked against SQLite)
# =========================================================

elif st.session_state.stage == "pattern":

    if not st.session_state.physical_grid:
        st.session_state.physical_grid = generate_grid()

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Enter Your Security Pattern</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Layout is shuffled every login — tap your memorized sequence</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Your pattern is not displayed anywhere. Tap the numbers you memorized, "
        "in order, wherever they appear on the shuffled grid below."
    )

    for i, number in enumerate(st.session_state.physical_grid):
        if i % 3 == 0:
            cols = st.columns(3)
        with cols[i % 3]:
            if number in st.session_state.entered_pattern:
                position = st.session_state.entered_pattern.index(number) + 1
                label = f"✓ {number}  ({position})"
            else:
                label = str(number)

            if st.button(label, key=f"login_pattern_{i}_{number}", use_container_width=True):
                if number not in st.session_state.entered_pattern:
                    st.session_state.entered_pattern.append(number)
                    st.rerun()

    entered_text = " → ".join(str(n) for n in st.session_state.entered_pattern) or "—"
    st.write(f"**Pattern entered:** {entered_text}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear Pattern", use_container_width=True):
            st.session_state.entered_pattern = []
            st.rerun()
    with c2:
        if st.button("Verify Pattern", type="primary", use_container_width=True):

            if not st.session_state.otp_verified:
                st.error("OTP verification is required first.")
            elif verify_pattern_attempt(st.session_state.mobile_number, st.session_state.entered_pattern):
                st.session_state.pattern_verified = True
                st.session_state.login_status = True
                st.session_state.stage = "dashboard"
                st.rerun()
            else:
                st.session_state.pattern_attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.pattern_attempts

                # Reshuffle on every attempt, failed or not, so a captured
                # screen from this try is useless on the next one.
                st.session_state.physical_grid = generate_grid()
                st.session_state.entered_pattern = []

                if remaining > 0:
                    st.error("Incorrect pattern.")
                    st.warning(f"Remaining attempts: {remaining}")
                    st.rerun()
                else:
                    st.session_state.stage = "pattern_failed"
                    st.rerun()

    st.caption(f"Pattern attempts: {st.session_state.pattern_attempts}/{MAX_ATTEMPTS}")


# =========================================================
# PATTERN FAILED
# =========================================================

elif st.session_state.stage == "pattern_failed":

    st.error("Pattern authentication failed. Please restart login.")
    st.warning("Please restart the authentication process.")

    if st.button("Restart Login", type="primary", use_container_width=True):
        restart_login()


# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state.stage == "dashboard":

    st.markdown('<div class="dashboard-banner">', unsafe_allow_html=True)
    st.markdown("<h1>Welcome back! 👋</h1>", unsafe_allow_html=True)
    st.write("Your secure digital documents are available below.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.success("All authentication factors verified successfully.")

    if st.button("🚪 Logout", type="primary", use_container_width=True):
        logout()

    st.subheader("Secure DigiLocker Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", "10")
    with col2:
        st.metric("Verified", "10")
    with col3:
        st.metric("Shared", "2")

    st.divider()

    nav = st.selectbox(
        "Navigation",
        ["Home", "My Documents", "Issued Documents", "Shared Documents", "Profile", "Help"]
    )

    if nav == "Home":
        st.subheader("Important Documents")
        st.write("Access your important digital documents from one place.")

    elif nav == "My Documents":
        st.subheader("My Documents")

    elif nav == "Issued Documents":
        st.subheader("Issued Documents")
        st.info("These are sample documents for the academic prototype.")

    elif nav == "Shared Documents":
        st.subheader("Shared Documents")
        st.info("No real documents are shared. This is demo data.")

    elif nav == "Profile":
        st.subheader("Profile")
        st.write("Account: Demo User")
        st.write("Mobile Number: ******" + st.session_state.mobile_number[-4:])
        st.write("Authentication: PIN + OTP + Enrolled Pattern")
        st.write("Account Type: Academic Prototype")

        st.divider()
        st.caption("Demo control — not part of the normal user flow:")
        if st.button("Reset my enrolled pattern (demo only)"):
            delete_pattern(st.session_state.mobile_number)
            st.success("Pattern enrollment cleared. You'll be asked to create a new one on next login.")

    elif nav == "Help":
        st.subheader("Help & Security Information")

        with st.expander("Security PIN"):
            st.write("The Security PIN acts as the primary authentication factor.")

        with st.expander("OTP Security"):
            st.write("A cryptographically secure random 6-digit OTP is generated.")
            st.write("Only an HMAC-SHA256 representation is stored for verification.")
            st.write("The OTP expires after 60 seconds and becomes invalid after successful use.")

        with st.expander("Enrolled Pattern"):
            st.write(
                "Chosen once by the user and stored as a salted, peppered "
                "PBKDF2-SHA256 hash in a persistent database — never in "
                "plain text, and never redisplayed after saving."
            )
            st.write(
                "The on-screen grid layout is reshuffled on every login "
                "attempt, including failed ones, so a captured screen from "
                "one attempt doesn't help on the next."
            )
            st.write(
                "This persists across sessions and devices, unlike the "
                "PIN and OTP state above, because a step-up factor only "
                "means something if it survives beyond one browser tab."
            )

        with st.expander("Combined Authentication"):
            st.write("Authentication requires the correct Security PIN, OTP and enrolled Pattern.")

        with st.expander("Prototype Limitation"):
            st.write(
                "This is an academic simulation. It does not connect "
                "to DigiLocker, UIDAI, SMS gateways or government databases. "
                "It also does not defend against server-side authorization "
                "flaws (e.g. API parameter tampering, IDOR) — those require "
                "fixing session/state validation on the server independently "
                "of any additional authentication factor."
            )

    st.divider()
    st.subheader("Important Documents")

    for i in range(0, len(DOCUMENTS), 2):
        cols = st.columns(2)
        for j in range(2):
            index = i + j
            if index >= len(DOCUMENTS):
                continue
            doc = DOCUMENTS[index]
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"### {doc['name']}")
                    st.write(f"**Issuing Authority:** {doc['authority']}")
                    st.write(f"**Issue Date:** {doc['date']}")

                    if doc["status"] == "Verified":
                        st.success("✓ Verified")
                    else:
                        st.info(doc["status"])

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View", key=f"view_{index}", use_container_width=True):
                            st.info(f"Viewing sample document: {doc['name']}")
                    with b2:
                        sample_document = (
                            "SECURE DIGILOCKER ACADEMIC PROTOTYPE\n\n"
                            f"Document: {doc['name']}\n"
                            f"Issuing Authority: {doc['authority']}\n"
                            f"Status: {doc['status']}\n"
                            f"Issue Date: {doc['date']}\n\n"
                            "Dummy document for demonstration only."
                        )
                        clean_name = doc["name"]
                        for prefix in ["🪪 ", "🚗 ", "🗳️ ", "🎓 ", "📄 ", "🏥 ", "🏦 ", "📑 "]:
                            clean_name = clean_name.replace(prefix, "")

                        st.download_button(
                            "Download",
                            data=sample_document,
                            file_name=clean_name.replace(" ", "_") + "_sample.txt",
                            mime="text/plain",
                            key=f"download_{index}",
                            use_container_width=True
                        )

    st.markdown(
        '<div class="footer">Secure DigiLocker | Academic Prototype | Dummy documents only</div>',
        unsafe_allow_html=True
    )
