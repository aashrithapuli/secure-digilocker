import streamlit as st
import secrets
import hashlib
import hmac
import time

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="TriLock | Multi-Factor Vault",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CONFIGURATION & CONSTANTS
# =========================================================
DEMO_PIN = "123456"
HMAC_SECRET = b"secure-digilocker-academic-demo-secret"
MAX_ATTEMPTS = 3
OTP_VALID_SECONDS = 60

DOCUMENTS = [
    {"name": "Aadhaar Card", "icon": "🪪", "authority": "UIDAI", "status": "Verified", "date": "15 Jan 2025"},
    {"name": "Driving Licence", "icon": "🚗", "authority": "Transport Department", "status": "Verified", "date": "20 Feb 2025"},
    {"name": "Voter ID", "icon": "🗳️", "authority": "Election Commission", "status": "Verified", "date": "10 Mar 2025"},
    {"name": "Class 10 Certificate", "icon": "🎓", "authority": "Education Board", "status": "Verified", "date": "05 Apr 2025"},
    {"name": "Class 12 Certificate", "icon": "🎓", "authority": "Education Board", "status": "Verified", "date": "12 May 2025"},
    {"name": "Degree Certificate", "icon": "📜", "authority": "University", "status": "Verified", "date": "15 Jun 2025"},
    {"name": "PAN Card", "icon": "📄", "authority": "Income Tax Department", "status": "Verified", "date": "18 Jul 2025"},
    {"name": "Health Certificate", "icon": "🏥", "authority": "Health Department", "status": "Verified", "date": "22 Aug 2025"},
    {"name": "Income Certificate", "icon": "🏦", "authority": "Revenue Department", "status": "Verified", "date": "30 Sep 2025"},
    {"name": "Other Documents", "icon": "📑", "authority": "Various Authorities", "status": "Available", "date": "01 Oct 2025"}
]

# =========================================================
# SYSTEM INJECTED STYLES (Aesthetic Glassmorphism Theme)
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 100%);
        color: #f8fafc;
    }

    /* Glassmorphism Card Wrapper */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }

    .glass-card-sm {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Header Styling */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 24px;
    }

    /* Pattern Sequence Output */
    .pattern-display {
        background: rgba(15, 23, 42, 0.8);
        border: 1px dashed #6366f1;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #a5b4fc;
        letter-spacing: 0.1em;
        margin: 16px 0;
    }

    /* Primary Buttons Styling */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
    }

    /* Step Indicator Badges */
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE INITIALIZATION
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
    "current_pattern": [],
    "entered_pattern": [],
    "pattern_attempts": 0,
    "pattern_verified": False,
    "login_status": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# UTILITY & SECURITY LOGIC
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

def generate_pattern():
    length = secrets.choice([3, 4, 5])
    return secrets.SystemRandom().sample(list(range(1, 10)), length)

def create_new_otp():
    otp = generate_otp()
    st.session_state.demo_otp = otp
    st.session_state.otp_hash = otp_digest(otp)
    st.session_state.otp_created_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False
    st.session_state.current_pattern = []
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False
    st.session_state.stage = "otp"

def start_authentication(mobile):
    st.session_state.mobile_number = mobile
    st.session_state.pin_attempts = 0
    st.session_state.pin_verified = False
    st.session_state.stage = "pin"

def restart_login():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()

def otp_remaining():
    if not st.session_state.otp_created_at:
        return 0
    elapsed = int(time.time() - st.session_state.otp_created_at)
    return max(0, OTP_VALID_SECONDS - elapsed)

# =========================================================
# UI HEADER COMPONENT
# =========================================================
st.markdown("""
    <div style="text-align: center; padding-top: 10px;">
        <span class="badge-pill">🇮🇳 Academic Security Framework</span>
        <h1 class="hero-title">TriLock Authentication</h1>
        <p class="hero-subtitle">Next-Generation Multi-Factor Identity Protection</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# STEP PROGRESS RENDERING
# =========================================================
def render_step_progress(current_stage):
    stages = ["mobile", "pin", "otp", "pattern"]
    if current_stage not in stages:
        return
    idx = stages.index(current_stage)
    
    cols = st.columns(4)
    labels = ["Mobile", "Security PIN", "OTP Code", "Dynamic Pattern"]
    
    for i in range(4):
        with cols[i]:
            if i < idx:
                st.caption(f"✓ {labels[i]}")
                st.progress(100)
            elif i == idx:
                st.caption(f"🔵 **{labels[i]}**")
                st.progress(50)
            else:
                st.caption(f"⚪ {labels[i]}")
                st.progress(0)

# =========================================================
# STAGE 1: MOBILE ENTRY
# =========================================================
if st.session_state.stage == "mobile":
    render_step_progress("mobile")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Step 1: Account Access")
    st.write("Enter your registered phone number to initiate zero-trust validation.")
    
    mobile = st.text_input("Mobile Number", placeholder="10-digit number", max_chars=10)
    
    if st.button("Continue to PIN Entry →", type="primary", use_container_width=True):
        cleaned = mobile.strip().replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) != 10 or cleaned[0] not in "6789":
            st.error("Please enter a valid 10-digit Indian mobile number.")
        else:
            start_authentication(cleaned)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# STAGE 2: PIN ENTRY
# =========================================================
elif st.session_state.stage == "pin":
    render_step_progress("pin")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Step 2: Security PIN")
    st.caption("Default Demo Security PIN: `123456`")
    
    pin = st.text_input("6-Digit PIN", type="password", max_chars=6, placeholder="••••••")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.stage = "mobile"
            st.rerun()
    with col2:
        if st.button("Verify PIN", type="primary", use_container_width=True):
            if not pin.isdigit() or len(pin) != 6:
                st.error("Enter a valid 6-digit numerical PIN.")
            elif hmac.compare_digest(hash_pin(pin), hash_pin(DEMO_PIN)):
                st.session_state.pin_verified = True
                create_new_otp()
                st.rerun()
            else:
                st.session_state.pin_attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.pin_attempts
                if remaining > 0:
                    st.error(f"Invalid PIN. Attempts remaining: {remaining}")
                else:
                    st.session_state.stage = "locked"
                    st.rerun()
                    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# STAGE 3: OTP VERIFICATION
# =========================================================
elif st.session_state.stage == "otp":
    if st_autorefresh is not None:
        st_autorefresh(interval=1000, key="otp_timer")
        
    remaining = otp_remaining()
    render_step_progress("otp")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Step 3: One-Time Password")
    
    # Display active OTP for academic demonstration
    st.info(f"🔑 **Simulated Gateway Dispatch OTP:** `{st.session_state.demo_otp}`")
    
    st.caption(f"Time Remaining: **{remaining}s**")
    st.progress(remaining / OTP_VALID_SECONDS)
    
    if remaining <= 0:
        st.error("The OTP has expired.")
        if st.button("Request New OTP", type="primary", use_container_width=True):
            create_new_otp()
            st.rerun()
    else:
        otp_input = st.text_input("Enter Received OTP", max_chars=6, placeholder="6-digit code")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("Resend OTP", use_container_width=True):
                create_new_otp()
                st.rerun()
        with c2:
            if st.button("Authenticate OTP", type="primary", use_container_width=True):
                if verify_otp(otp_input):
                    st.session_state.otp_used = True
                    st.session_state.otp_verified = True
                    st.session_state.current_pattern = generate_pattern()
                    st.session_state.entered_pattern = []
                    st.session_state.stage = "pattern"
                    st.rerun()
                else:
                    st.session_state.otp_attempts += 1
                    rem = MAX_ATTEMPTS - st.session_state.otp_attempts
                    if rem > 0:
                        st.error(f"Incorrect OTP. {rem} attempts left.")
                    else:
                        st.error("Maximum attempts reached. Generating new OTP.")
                        create_new_otp()
                        st.rerun()
                        
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# STAGE 4: DYNAMIC PATTERN MATRIX
# =========================================================
elif st.session_state.stage == "pattern":
    render_step_progress("pattern")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Step 4: Dynamic Pattern Match")
    st.write("Memorize the sequence below and reproduce it using the keypad grid:")
    
    pattern_str = " → ".join(str(x) for x in st.session_state.current_pattern)
    st.markdown(f'<div class="pattern-display">{pattern_str}</div>', unsafe_allow_html=True)
    
    # 3x3 Dynamic Grid
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            val = r * 3 + c + 1
            with cols[c]:
                if val in st.session_state.entered_pattern:
                    idx = st.session_state.entered_pattern.index(val) + 1
                    lbl = f"✓ {val} (#{idx})"
                else:
                    lbl = f"{val}"
                    
                if st.button(lbl, key=f"btn_pat_{val}", use_container_width=True):
                    if val not in st.session_state.entered_pattern:
                        if len(st.session_state.entered_pattern) < len(st.session_state.current_pattern):
                            st.session_state.entered_pattern.append(val)
                            st.rerun()

    entered_str = " → ".join(str(x) for x in st.session_state.entered_pattern) if st.session_state.entered_pattern else "—"
    st.write(f"**Current Input:** `{entered_str}`")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset Entry", use_container_width=True):
            st.session_state.entered_pattern = []
            st.rerun()
    with col2:
        if st.button("Finalize Verification", type="primary", use_container_width=True):
            if st.session_state.entered_pattern == st.session_state.current_pattern:
                st.session_state.pattern_verified = True
                st.session_state.login_status = True
                st.session_state.stage = "dashboard"
                st.rerun()
            else:
                st.session_state.pattern_attempts += 1
                st.session_state.entered_pattern = []
                rem = MAX_ATTEMPTS - st.session_state.pattern_attempts
                if rem > 0:
                    st.error(f"Pattern mismatch. Attempts remaining: {rem}")
                else:
                    st.session_state.stage = "pattern_failed"
                    st.rerun()
                    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# LOCKOUT & FAILURE STATES
# =========================================================
elif st.session_state.stage in ["locked", "pattern_failed"]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.error("⚠️ Access Denied: Authentication Threshold Exceeded")
    st.write("For your security, the session was terminated due to consecutive failed attempts.")
    if st.button("Restart Session", type="primary", use_container_width=True):
        restart_login()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# STAGE 5: DASHBOARD
# =========================================================
elif st.session_state.stage == "dashboard":
    st.balloons()
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.title("Welcome to Your Secure Vault")
    st.caption("3-Factor Identity Attestation Complete: PIN ✓ | OTP ✓ | Dynamic Pattern ✓")
    
    if st.button("🚪 Terminate Session & Logout", type="primary"):
        restart_login()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Document Grid
    st.subheader("Issued Digital Credentials")
    
    for i in range(0, len(DOCUMENTS), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(DOCUMENTS):
                doc = DOCUMENTS[idx]
                with cols[j]:
                    st.markdown(f"""
                        <div class="glass-card-sm">
                            <h4>{doc['icon']} {doc['name']}</h4>
                            <p style="color:#94a3b8; font-size:0.85rem; margin-bottom: 8px;">
                                Authority: {doc['authority']}<br>
                                Date: {doc['date']}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View", key=f"view_{idx}", use_container_width=True):
                            st.toast(f"Opening {doc['name']}...")
                    with b2:
                        st.download_button(
                            "Get File",
                            data=f"TriLock Credential: {doc['name']}\nIssued by: {doc['authority']}",
                            file_name=f"{doc['name'].lower().replace(' ', '_')}.txt",
                            key=f"dl_{idx}",
                            use_container_width=True
                        )

# =========================================================
# FOOTER
# =========================================================
st.markdown("<br><hr><center><small style='color:#64748b;'>TriLock Zero-Trust Framework • Academic Architecture Prototype</small></center>", unsafe_allow_html=True)
