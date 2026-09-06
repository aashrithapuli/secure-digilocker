import streamlit as st
import secrets
import hashlib
import hmac
import time
import random

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Demo configuration
# -----------------------------
OTP_EXPIRY_SECONDS = 60
MAX_OTP_ATTEMPTS = 3
DEMO_HMAC_SECRET = b"secure-digilocker-academic-demo-secret"

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "page": "login",
    "mobile": "",
    "enrolled_pattern": [],
    "pattern_selection": [],
    "physical_grid": [],
    "otp_hash": "",
    "otp_created": 0.0,
    "otp_attempts": 0,
    "otp_used": False,
    "otp_verified": False,
    "pattern_verified": False,
    "authenticated": False,
    "demo_otp": "",
    "otp_blocked": False,
    "font_scale": 1.0,
    "documents": [
        {
            "name": "Aadhaar Card",
            "authority": "UIDAI",
            "status": "Available",
            "date": "15 Jan 2026",
            "icon": "🪪",
        },
        {
            "name": "Driving Licence",
            "authority": "Transport Department",
            "status": "Available",
            "date": "02 Feb 2026",
            "icon": "🚗",
        },
        {
            "name": "Voter ID",
            "authority": "Election Commission",
            "status": "Available",
            "date": "20 Feb 2026",
            "icon": "🗳️",
        },
        {
            "name": "Class 10 Certificate",
            "authority": "Education Board",
            "status": "Available",
            "date": "10 Mar 2026",
            "icon": "🎓",
        },
        {
            "name": "Class 12 Certificate",
            "authority": "Education Board",
            "status": "Available",
            "date": "12 Mar 2026",
            "icon": "🎓",
        },
        {
            "name": "Degree Certificate",
            "authority": "University",
            "status": "Available",
            "date": "18 Apr 2026",
            "icon": "🎓",
        },
        {
            "name": "PAN Card",
            "authority": "Income Tax Department",
            "status": "Available",
            "date": "22 Apr 2026",
            "icon": "📄",
        },
        {
            "name": "Income Certificate",
            "authority": "Revenue Department",
            "status": "Available",
            "date": "05 May 2026",
            "icon": "🏦",
        },
    ],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# CSS
# -----------------------------
scale = st.session_state.font_scale

st.markdown(
    f"""
    <style>
    :root {{
        --primary: #5636d9;
        --primary-dark: #3d24a8;
        --lavender: #f3efff;
        --navy: #10236b;
        --text: #172033;
        --muted: #687087;
        --border: #d8dce8;
        --success: #167447;
        --danger: #b42318;
    }}

    html, body, [class*="css"] {{
        font-size: {scale}rem;
    }}

    .stApp {{
        background: var(--lavender);
    }}

    [data-testid="stHeader"] {{
        background: white;
    }}

    .govbar {{
        width: 100%;
        background: var(--navy);
        color: white;
        padding: 10px 18px;
        font-weight: 700;
        font-size: 14px;
    }}

    .brandbar {{
        background: white;
        border-bottom: 1px solid #e4e4ec;
        padding: 17px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .brand-icon {{
        width: 45px;
        height: 45px;
        border-radius: 12px;
        background: #ede8ff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
    }}

    .brand-name {{
        font-size: 25px;
        font-weight: 800;
        color: var(--primary);
        line-height: 1.1;
    }}

    .brand-sub {{
        color: var(--muted);
        font-size: 13px;
        margin-top: 4px;
    }}

    .prototype {{
        display: inline-block;
        margin-left: 7px;
        padding: 3px 7px;
        border-radius: 10px;
        background: #fff1c7;
        color: #704d00;
        font-size: 10px;
        vertical-align: middle;
    }}

    .login-card {{
        background: white;
        border: 1px solid #dddde7;
        border-radius: 18px;
        padding: 30px;
        margin: 34px auto 18px auto;
        box-shadow: 0 8px 28px rgba(50, 38, 100, 0.08);
        max-width: 560px;
    }}

    .login-title {{
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 7px;
    }}

    .login-subtitle {{
        color: var(--muted);
        font-size: 15px;
        margin-bottom: 22px;
    }}

    .section-card {{
        background: white;
        border: 1px solid #dddde7;
        border-radius: 18px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(50, 38, 100, 0.06);
    }}

    .section-title {{
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 7px;
    }}

    .helper {{
        color: var(--muted);
        font-size: 14px;
        line-height: 1.5;
    }}

    .info-box {{
        background: #eef4ff;
        border-left: 4px solid #3d75d8;
        border-radius: 8px;
        padding: 13px 15px;
        color: #174a91;
        margin: 12px 0 18px 0;
    }}

    .demo-box {{
        background: #fff8e1;
        border: 1px solid #f1d889;
        border-radius: 10px;
        padding: 14px;
        margin: 12px 0;
    }}

    .demo-otp {{
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 6px;
        text-align: center;
        color: var(--primary-dark);
        padding: 7px;
    }}

    .sequence {{
        background: #f5f3ff;
        border-radius: 10px;
        padding: 13px;
        text-align: center;
        font-size: 19px;
        font-weight: 800;
        color: var(--primary-dark);
        margin: 14px 0;
    }}

    .doc-card {{
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 17px;
        margin-bottom: 14px;
        box-shadow: 0 3px 12px rgba(50, 38, 100, 0.05);
    }}

    .doc-icon {{
        font-size: 31px;
    }}

    .doc-title {{
        font-size: 18px;
        font-weight: 800;
        color: #182033;
    }}

    .doc-meta {{
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }}

    .status {{
        display: inline-block;
        padding: 4px 9px;
        border-radius: 12px;
        background: #e6f7ee;
        color: var(--success);
        font-size: 12px;
        font-weight: 700;
    }}

    .footer {{
        text-align: center;
        color: #72798c;
        font-size: 12px;
        padding: 25px 10px 35px 10px;
    }}

    div.stButton > button {{
        min-height: 48px;
        border-radius: 10px;
        font-weight: 700;
        width: 100%;
    }}

    .pattern-note {{
        text-align: center;
        color: var(--muted);
        font-size: 13px;
        margin-top: 6px;
    }}

    @media (max-width: 600px) {{
        .login-card, .section-card {{
            padding: 18px;
            border-radius: 14px;
        }}

        .login-title {{
            font-size: 24px;
        }}

        .brand-name {{
            font-size: 21px;
        }}

        .govbar {{
            font-size: 12px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Common UI
# -----------------------------
def render_header():
    st.markdown(
        """
        <div class="govbar">🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services</div>
        <div class="brandbar">
            <div class="brand-icon">🔐</div>
            <div>
                <div class="brand-name">
                    Secure DigiLocker
                    <span class="prototype">ACADEMIC PROTOTYPE</span>
                </div>
                <div class="brand-sub">Secure digital document access</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            Secure DigiLocker is an independent academic prototype.<br>
            It does not connect to or represent the official DigiLocker service.
        </div>
        """,
        unsafe_allow_html=True,
    )


def clear_pattern():
    st.session_state.pattern_selection = []


def generate_physical_grid():
    values = list(range(1, 10))
    random.SystemRandom().shuffle(values)
    return values


def hash_otp(otp):
    return hmac.new(
        DEMO_HMAC_SECRET,
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def otp_is_expired():
    if not st.session_state.otp_created:
        return True
    return time.time() - st.session_state.otp_created >= OTP_EXPIRY_SECONDS


def generate_new_otp():
    otp = f"{secrets.randbelow(1000000):06d}"
    st.session_state.otp_hash = hash_otp(otp)
    st.session_state.otp_created = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False
    st.session_state.pattern_verified = False
    st.session_state.otp_blocked = False
    st.session_state.demo_otp = otp
    st.session_state.pattern_selection = []


def start_login(mobile):
    st.session_state.mobile = mobile
    generate_new_otp()
    st.session_state.page = "otp"
    st.rerun()


def reset_to_login():
    st.session_state.page = "login"
    st.session_state.otp_verified = False
    st.session_state.pattern_verified = False
    st.session_state.pattern_selection = []
    st.session_state.otp_hash = ""
    st.session_state.demo_otp = ""
    st.session_state.otp_created = 0
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_blocked = False
    st.rerun()


# -----------------------------
# Login
# -----------------------------
def login_page():
    render_header()

    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Login or Create Account</div>
            <div class="login-subtitle">Enter your mobile number to proceed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.enrolled_pattern:
        st.markdown(
            '<div class="info-box">Create your personal security pattern before logging in.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Create Security Pattern", type="primary"):
            st.session_state.page = "enroll"
            st.rerun()

    mobile = st.text_input(
        "Mobile number",
        value=st.session_state.mobile,
        placeholder="10-digit mobile number",
        max_chars=10,
    )

    st.caption("For this academic prototype, use any valid 10-digit Indian mobile number.")

    st.markdown(
        "By continuing, I agree to the Terms of Service for this academic prototype."
    )

    if st.button("Continue", type="primary"):
        if not mobile.isdigit() or len(mobile) != 10 or mobile[0] not in "6789":
            st.error("Please enter a valid 10-digit Indian mobile number.")
        elif not st.session_state.enrolled_pattern:
            st.warning("Please create your security pattern first.")
        else:
            start_login(mobile)

    st.markdown("---")
    st.markdown("<div style='text-align:center;font-weight:700;'>OR</div>", unsafe_allow_html=True)

    if st.button("▣  Login using QR Code"):
        st.info("QR login is represented as a UI placeholder in this academic prototype.")

    st.markdown(
        "<div style='text-align:center;margin-top:12px;'>"
        "♿ Accessibility: use the controls below to change text size."
        "</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("A−"):
            st.session_state.font_scale = max(0.85, st.session_state.font_scale - 0.05)
            st.rerun()
    with c2:
        if st.button("A"):
            st.session_state.font_scale = 1.0
            st.rerun()
    with c3:
        if st.button("A+"):
            st.session_state.font_scale = min(1.25, st.session_state.font_scale + 0.05)
            st.rerun()

    render_footer()


# -----------------------------
# Pattern enrollment
# -----------------------------
def enrollment_page():
    render_header()

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Create Your Security Pattern</div>
            <div class="helper">
                Choose a sequence of numbers that you can remember.
                This is your personal logical pattern. It will be used during login.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-box"><b>Example:</b> You may choose 2 → 5 → 8 → 9. '
        "Do not use a pattern that is easy for others to guess.</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i in range(9):
        number = i + 1
        with cols[i % 3]:
            selected = number in st.session_state.pattern_selection
            label = f"✓ {number}" if selected else str(number)

            if st.button(
                label,
                key=f"enroll_{number}",
                type="primary" if selected else "secondary",
            ):
                if number in st.session_state.pattern_selection:
                    st.session_state.pattern_selection.remove(number)
                else:
                    st.session_state.pattern_selection.append(number)
                st.rerun()

    if st.session_state.pattern_selection:
        sequence = " → ".join(map(str, st.session_state.pattern_selection))
    else:
        sequence = "No numbers selected"

    st.markdown(
        f'<div class="sequence">Pattern selected: {sequence}</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear Pattern"):
            clear_pattern()
            st.rerun()
    with c2:
        if st.button("Save Pattern", type="primary"):
            if len(st.session_state.pattern_selection) < 3:
                st.error("Choose at least 3 numbers for your pattern.")
            elif len(st.session_state.pattern_selection) > 9:
                st.error("A pattern can contain a maximum of 9 numbers.")
            else:
                st.session_state.enrolled_pattern = st.session_state.pattern_selection.copy()
                st.session_state.pattern_selection = []
                st.session_state.page = "login"
                st.success("Security pattern saved successfully.")
                st.rerun()

    if st.button("← Back to Login"):
        st.session_state.pattern_selection = []
        st.session_state.page = "login"
        st.rerun()

    render_footer()


# -----------------------------
# OTP verification
# -----------------------------
def otp_page():
    render_header()

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Verify Your Mobile Number</div>
            <div class="helper">
                Enter the 6-digit OTP generated for this academic demonstration.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.otp_created:
        generate_new_otp()

    remaining = max(0, int(OTP_EXPIRY_SECONDS - (time.time() - st.session_state.otp_created)))

    st.markdown(
        f"""
        <div class="demo-box">
            <b>Demo OTP</b><br>
            In a real system this would be sent through SMS.
            <div class="demo-otp">{st.session_state.demo_otp}</div>
            <div style="text-align:center;">Expires in approximately {remaining} seconds</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if otp_is_expired():
        st.error("This OTP has expired.")
        if st.button("Generate New OTP", type="primary"):
            generate_new_otp()
            st.rerun()
        if st.button("← Back to Login"):
            reset_to_login()
        render_footer()
        return

    if st.session_state.otp_blocked:
        st.error("Verification is blocked after 3 incorrect attempts.")
        if st.button("Generate New OTP", type="primary"):
            generate_new_otp()
            st.rerun()
        render_footer()
        return

    otp_input = st.text_input(
        "Enter OTP",
        max_chars=6,
        placeholder="6-digit OTP",
    )

    if st.button("Verify OTP", type="primary"):
        if not otp_input.isdigit() or len(otp_input) != 6:
            st.error("Please enter exactly 6 digits.")
        elif otp_is_expired():
            st.error("OTP expired. Please generate a new OTP.")
        elif st.session_state.otp_used:
            st.error("This OTP has already been used.")
        else:
            entered_hash = hash_otp(otp_input)
            if hmac.compare_digest(entered_hash, st.session_state.otp_hash):
                st.session_state.otp_verified = True
                st.session_state.otp_used = True
                st.session_state.page = "pattern"
                st.session_state.physical_grid = generate_physical_grid()
                st.session_state.pattern_selection = []
                st.rerun()
            else:
                st.session_state.otp_attempts += 1
                attempts_left = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts

                if attempts_left <= 0:
                    st.session_state.otp_blocked = True
                    st.error("Maximum OTP attempts reached. Generate a new OTP.")
                else:
                    st.error(f"Incorrect OTP. Attempts remaining: {attempts_left}")

    if st.button("Resend / Generate New OTP"):
        generate_new_otp()
        st.rerun()

    if st.button("Cancel Login"):
        reset_to_login()

    render_footer()


# -----------------------------
# Dynamic pattern verification
# -----------------------------
def pattern_page():
    render_header()

    if not st.session_state.physical_grid:
        st.session_state.physical_grid = generate_physical_grid()

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Dynamic Pattern Verification</div>
            <div class="helper">
                The physical arrangement changes on every login.
                Select the same numbers you chose during enrollment.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-box">Your remembered logical pattern is not displayed here. '
        "Select your own sequence from the shuffled numbered grid.</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, number in enumerate(st.session_state.physical_grid):
        with cols[i % 3]:
            selected = number in st.session_state.pattern_selection
            label = f"✓ {number}" if selected else str(number)

            if st.button(
                label,
                key=f"login_pattern_{i}_{number}",
                type="primary" if selected else "secondary",
            ):
                if number in st.session_state.pattern_selection:
                    st.session_state.pattern_selection.remove(number)
                else:
                    st.session_state.pattern_selection.append(number)
                st.rerun()

    entered = st.session_state.pattern_selection
    sequence = " → ".join(map(str, entered)) if entered else "No numbers selected"

    st.markdown(
        f'<div class="sequence">Pattern entered: {sequence}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="pattern-note">For the prototype, the numbered grid is touch-friendly '
        "and works on Android browsers.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear Pattern"):
            clear_pattern()
            st.rerun()

    with c2:
        if st.button("Verify Pattern", type="primary"):
            if entered == st.session_state.enrolled_pattern:
                st.session_state.pattern_verified = True
                st.session_state.authenticated = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Authentication failed. The pattern does not match.")

    render_footer()


# -----------------------------
# Dashboard
# -----------------------------
def dashboard_page():
    render_header()

    top1, top2 = st.columns([4, 1])
    with top1:
        st.markdown(
            """
            <div style="margin-top:24px;">
                <div class="section-title">Welcome back!</div>
                <div class="helper">Your secure digital documents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top2:
        if st.button("Logout"):
            reset_to_login()

    st.markdown(
        """
        <div class="info-box">
            <b>Authentication complete</b><br>
            OTP verification and dynamic pattern verification were successful.
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav = st.selectbox(
        "Navigation",
        [
            "Home",
            "My Documents",
            "Issued Documents",
            "Shared Documents",
            "Profile",
            "Help",
        ],
    )

    if nav == "Profile":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Profile")
        st.write("Mobile: +91 ••••••" + st.session_state.mobile[-4:])
        st.write("Security pattern: Enabled")
        st.write("OTP protection: Enabled")
        st.markdown("</div>", unsafe_allow_html=True)
        render_footer()
        return

    if nav == "Help":
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Help & Security</div>
                <div class="helper">
                    This prototype demonstrates OTP expiry, limited attempts,
                    one-time OTP usage, replay prevention, and dynamic
                    physical-to-logical pattern mapping.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_footer()
        return

    if nav == "Shared Documents":
        st.info("No sample shared documents are available.")
        render_footer()
        return

    if nav == "Issued Documents":
        st.info("Sample issued documents are shown below.")
    elif nav == "My Documents":
        st.info("Your sample digital documents are shown below.")
    else:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Your Documents</div>
                <div class="helper">
                    Sample documents for demonstration only. No real government
                    documents or sensitive personal data are stored.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for doc in st.session_state.documents:
        st.markdown(
            f"""
            <div class="doc-card">
                <div class="doc-icon">{doc["icon"]}</div>
                <div class="doc-title">{doc["name"]}</div>
                <div class="doc-meta">
                    Issuing authority: {doc["authority"]}<br>
                    Issue date: {doc["date"]}<br>
                    <span class="status">{doc["status"]}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("View", key=f"view_{doc['name']}"):
                st.info(
                    f"Demo preview: {doc['name']} issued by {doc['authority']}."
                )
        with c2:
            if st.button("Download", key=f"download_{doc['name']}"):
                st.info("Demo only — no real document is downloaded.")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Security mechanisms used</div>
            <div class="helper">
                • 60-second OTP expiry<br>
                • Maximum 3 incorrect OTP attempts<br>
                • One-time OTP use<br>
                • Replay prevention<br>
                • Cryptographic OTP hashing/HMAC verification<br>
                • Custom enrolled logical pattern<br>
                • New physical grid arrangement for every login<br>
                • Combined OTP + dynamic pattern authentication
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_footer()


# -----------------------------
# App router
# -----------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "enroll":
    enrollment_page()
elif st.session_state.page == "otp":
    otp_page()
elif st.session_state.page == "pattern":
    pattern_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
else:
    st.session_state.page = "login"
    st.rerun()
