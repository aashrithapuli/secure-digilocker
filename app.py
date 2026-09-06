import streamlit as st
import secrets
import hashlib
import hmac
import time
import random

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

OTP_VALID_SECONDS = 60
MAX_OTP_ATTEMPTS = 3

DOCUMENTS = [
    {"name": "Aadhaar Card", "icon": "🪪", "authority": "UIDAI", "status": "Verified", "date": "15 Aug 2025"},
    {"name": "Driving Licence", "icon": "🚗", "authority": "Transport Department", "status": "Verified", "date": "08 Jun 2025"},
    {"name": "Voter ID", "icon": "🗳️", "authority": "Election Commission of India", "status": "Verified", "date": "20 Jan 2025"},
    {"name": "Class 10 Certificate", "icon": "🎓", "authority": "Education Board", "status": "Verified", "date": "12 May 2024"},
    {"name": "Class 12 Certificate", "icon": "🎓", "authority": "Education Board", "status": "Verified", "date": "25 May 2024"},
    {"name": "Degree Certificate", "icon": "🎓", "authority": "University", "status": "Available", "date": "30 Jul 2025"},
    {"name": "PAN Card", "icon": "📄", "authority": "Income Tax Department", "status": "Verified", "date": "03 Mar 2025"},
    {"name": "Health Certificate", "icon": "🏥", "authority": "Health Department", "status": "Available", "date": "18 Feb 2025"},
    {"name": "Income Certificate", "icon": "🏦", "authority": "Revenue Department", "status": "Available", "date": "10 Apr 2025"},
    {"name": "Other Documents", "icon": "📑", "authority": "Sample Authority", "status": "Available", "date": "01 Sep 2025"},
]

defaults = {
    "page": "login",
    "mobile": "",
    "otp_hash": "",
    "otp_created": 0.0,
    "otp_attempts": 0,
    "otp_used": False,
    "otp_blocked": False,
    "demo_otp": "",
    "physical_to_logical": {},
    "pattern_selected": [],
    "enrolled_pattern": [],
    "enrollment_selected": [],
    "authenticated": False,
    "nav": "Home",
    "font_scale": 1.0,
    "demo_mode": True,
    "pattern_error": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

HMAC_SECRET = b"secure-digilocker-academic-demo-key"


def otp_digest(otp):
    return hmac.new(HMAC_SECRET, otp.encode(), hashlib.sha256).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def create_mapping():
    nodes = list(range(1, 10))
    random.SystemRandom().shuffle(nodes)
    return {i: nodes[i] for i in range(9)}


def start_authentication(mobile):
    otp = generate_otp()
    st.session_state.mobile = mobile
    st.session_state.otp_hash = otp_digest(otp)
    st.session_state.otp_created = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_blocked = False
    st.session_state.demo_otp = otp
    st.session_state.physical_to_logical = create_mapping()
    st.session_state.pattern_selected = []
    st.session_state.pattern_error = ""
    st.session_state.page = "verify"


def otp_remaining():
    if not st.session_state.otp_created:
        return 0
    return max(0, OTP_VALID_SECONDS - int(time.time() - st.session_state.otp_created))


def reset_otp():
    start_authentication(st.session_state.mobile)


def logout():
    for key in [
        "mobile", "otp_hash", "otp_created", "otp_attempts", "otp_used",
        "otp_blocked", "demo_otp", "physical_to_logical", "pattern_selected",
        "enrolled_pattern", "enrollment_selected", "authenticated", "pattern_error"
    ]:
        if key in st.session_state:
            if isinstance(st.session_state[key], list):
                st.session_state[key] = []
            elif isinstance(st.session_state[key], dict):
                st.session_state[key] = {}
            elif isinstance(st.session_state[key], bool):
                st.session_state[key] = False
            elif isinstance(st.session_state[key], (int, float)):
                st.session_state[key] = 0
            else:
                st.session_state[key] = ""
    st.session_state.page = "login"
    st.session_state.nav = "Home"


st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{ font-size: {st.session_state.font_scale}em; }}
    .stApp {{ background: #f4f0ff; }}
    .top-government {{ background:#07185c; color:white; padding:9px 6%; font-weight:600; }}
    .brand-bar {{ background:white; padding:18px 6%; border-bottom:1px solid #ddd6f4; display:flex; align-items:center; gap:14px; }}
    .brand-icon {{ width:46px; height:46px; border-radius:12px; background:#6741f5; color:white; display:flex; align-items:center; justify-content:center; font-size:25px; }}
    .brand-name {{ color:#5132d5; font-size:1.65rem; font-weight:800; }}
    .brand-sub {{ color:#666; font-size:.72rem; }}
    .prototype {{ display:inline-block; padding:5px 10px; border-radius:15px; background:#fff3cd; color:#664d03; font-size:.72rem; margin-left:8px; }}
    .login-card {{ background:white; border:1px solid #ddd; border-radius:20px; padding:34px; box-shadow:0 8px 30px rgba(40,20,100,.10); max-width:560px; margin:28px auto; }}
    .login-title {{ font-size:2rem; font-weight:800; color:#111; }}
    .login-subtitle {{ color:#666; margin-bottom:18px; }}
    .info-box {{ padding:14px 16px; border-radius:12px; background:#f1edff; border-left:5px solid #6741f5; margin:12px 0; }}
    .otp-box {{ padding:18px; background:#fff8df; border:1px solid #e8d28a; border-radius:12px; margin:15px 0; text-align:center; }}
    .otp-number {{ font-size:2rem; font-weight:900; letter-spacing:7px; color:#4325bd; }}
    .timer {{ font-size:1.15rem; font-weight:800; color:#b42318; }}
    .dashboard-card {{ background:white; border:1px solid #ded9ef; border-radius:16px; padding:20px; min-height:180px; box-shadow:0 4px 16px rgba(40,20,100,.06); }}
    .doc-icon {{ font-size:2.1rem; }} .doc-name {{ font-size:1.1rem; font-weight:800; }}
    .doc-meta {{ color:#666; font-size:.88rem; margin:5px 0; }}
    .status {{ display:inline-block; padding:4px 9px; border-radius:10px; background:#e8f5e9; color:#176b2c; font-size:.78rem; font-weight:700; }}
    .dashboard-banner {{ background:linear-gradient(135deg,#5634dd,#7d5bea); color:white; padding:28px; border-radius:18px; margin-bottom:22px; }}
    .dashboard-banner h1 {{ margin:0; font-size:2rem; }}
    .footer {{ text-align:center; color:#666; padding:28px 10px; font-size:.82rem; }}
    @media (max-width:700px) {{
        .top-government {{ padding:8px 15px; font-size:.78rem; }}
        .brand-bar {{ padding:13px 15px; }}
        .brand-name {{ font-size:1.35rem; }}
        .login-card {{ margin:12px 4px; padding:22px 17px; border-radius:15px; }}
        .login-title {{ font-size:1.55rem; }}
        .dashboard-banner {{ padding:20px; }}
        .dashboard-banner h1 {{ font-size:1.5rem; }}
        button {{ min-height:48px !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="top-government">🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services</div>
    <div class="brand-bar">
        <div class="brand-icon">🔐</div>
        <div>
            <div class="brand-name">Secure DigiLocker <span class="prototype">ACADEMIC PROTOTYPE</span></div>
            <div class="brand-sub">Secure digital document access</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Accessibility")
    if st.button("A− Smaller text", use_container_width=True):
        st.session_state.font_scale = max(.85, st.session_state.font_scale - .05)
        st.rerun()
    if st.button("A+ Larger text", use_container_width=True):
        st.session_state.font_scale = min(1.30, st.session_state.font_scale + .05)
        st.rerun()
    st.session_state.demo_mode = st.checkbox("Demo Mode", value=st.session_state.demo_mode)
    st.markdown("---")
    st.info("Academic simulation only. Use dummy data. This is not an actual government service.")

# ---------------- ENROLLMENT ----------------
if not st.session_state.authenticated and st.session_state.page == "enroll":
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Create Your Security Pattern</div>
            <div class="login-subtitle">
                Choose a pattern that you can remember. It will be converted into a logical pattern
                and the physical positions will change on every login.
            </div>
            <div class="info-box">
                <b>How it works</b><br>
                Select at least 3 nodes. Your chosen logical sequence becomes your enrolled pattern.
                Remember the node numbers, not their physical positions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("### Choose your pattern")

        for row in range(3):
            cols = st.columns(3)
            for col_index in range(3):
                node = row * 3 + col_index + 1
                selected_pos = (
                    st.session_state.enrollment_selected.index(node) + 1
                    if node in st.session_state.enrollment_selected else None
                )
                label = f"✓ Node {node} ({selected_pos})" if selected_pos else f"● Node {node}"
                with cols[col_index]:
                    if st.button(
                        label,
                        key=f"enroll_{node}",
                        use_container_width=True,
                        disabled=node in st.session_state.enrollment_selected
                        or len(st.session_state.enrollment_selected) >= 9,
                    ):
                        st.session_state.enrollment_selected.append(node)
                        st.rerun()

        selected = st.session_state.enrollment_selected
        st.markdown(
            f'<div class="info-box"><b>Pattern selected:</b> '
            f'{" → ".join(map(str, selected)) if selected else "None"}</div>',
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Clear Pattern", use_container_width=True):
                st.session_state.enrollment_selected = []
                st.rerun()
        with b2:
            if st.button("Save Pattern", type="primary", use_container_width=True):
                if len(selected) < 3:
                    st.error("Choose at least 3 nodes.")
                else:
                    st.session_state.enrolled_pattern = selected[:]
                    st.session_state.enrollment_selected = []
                    st.session_state.page = "login"
                    st.success("Pattern enrolled successfully. You can now log in.")
                    st.rerun()

    st.markdown(
        '<div class="footer">Your pattern is stored only in this Streamlit session for this academic prototype.</div>',
        unsafe_allow_html=True,
    )

# ---------------- LOGIN ----------------
elif not st.session_state.authenticated and st.session_state.page == "login":
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Login or Create Account</div>
            <div class="login-subtitle">Enter your mobile number to proceed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])
    with center:
        if not st.session_state.enrolled_pattern:
            st.info("New user? Create your security pattern before logging in.")
            if st.button("Create Security Pattern", type="primary", use_container_width=True):
                st.session_state.page = "enroll"
                st.rerun()

        mobile = st.text_input(
            "Mobile number",
            placeholder="10-digit mobile number",
            max_chars=10,
        )

        st.caption("By continuing, I agree to the Terms of Service.")

        if st.button("Continue", type="primary", use_container_width=True):
            cleaned = mobile.strip().replace(" ", "")
            if not cleaned.isdigit() or len(cleaned) != 10:
                st.error("Please enter a valid 10-digit mobile number.")
            elif not st.session_state.enrolled_pattern:
                st.error("Please create your security pattern first.")
            else:
                start_authentication(cleaned)
                st.rerun()

        st.markdown(
            "<div style='text-align:center;margin:18px 0;color:#777;'>──────── OR ────────</div>",
            unsafe_allow_html=True,
        )

        if st.button("▣  Login using QR Code", use_container_width=True):
            st.info("QR login is simulated. No real QR authentication is performed.")

        st.markdown(
            '<div class="info-box"><b>🔐 Two-step authentication</b><br>'
            'OTP + your dynamic visual pattern are required.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="footer">Secure DigiLocker — Academic Prototype<br>Dummy data only.</div>',
        unsafe_allow_html=True,
    )

# ---------------- OTP + PATTERN ----------------
elif not st.session_state.authenticated and st.session_state.page == "verify":
    if st_autorefresh is not None:
        st_autorefresh(interval=1000, key="otp_timer")

    remaining = otp_remaining()

    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Secure Verification</div>
            <div class="login-subtitle">Complete both steps to access your documents.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("### Step 1 — OTP Verification")

        if st.session_state.otp_blocked:
            st.error("OTP verification is blocked after 3 incorrect attempts.")
            if st.button("Generate New OTP", type="primary", use_container_width=True):
                reset_otp()
                st.rerun()

        elif remaining == 0:
            st.error("This OTP has expired.")
            if st.button("Generate New OTP", type="primary", use_container_width=True):
                reset_otp()
                st.rerun()

        else:
            st.markdown(
                f'<div class="otp-box">'
                f'<div>Demo OTP — In a real system this would be sent through SMS.</div>'
                f'<div class="otp-number">{st.session_state.demo_otp}</div>'
                f'<div class="timer">Expires in {remaining} seconds</div></div>',
                unsafe_allow_html=True,
            )

            otp_input = st.text_input("Enter 6-digit OTP", max_chars=6, type="password")

            if st.button("Verify OTP", use_container_width=True):
                if not otp_input.isdigit() or len(otp_input) != 6:
                    st.error("Enter a valid 6-digit OTP.")
                elif remaining == 0:
                    st.error("OTP expired. Generate a new OTP.")
                elif st.session_state.otp_used:
                    st.error("This OTP has already been used.")
                else:
                    entered_hash = otp_digest(otp_input)
                    if hmac.compare_digest(entered_hash, st.session_state.otp_hash):
                        st.session_state.otp_used = True
                        st.success("OTP verified. Complete the visual pattern.")
                    else:
                        st.session_state.otp_attempts += 1
                        left_attempts = MAX_OTP_ATTEMPTS - st.session_state.otp_attempts
                        if left_attempts <= 0:
                            st.session_state.otp_blocked = True
                            st.error("OTP blocked after 3 incorrect attempts.")
                        else:
                            st.error(f"Incorrect OTP. {left_attempts} attempt(s) remaining.")

        st.markdown("---")
        st.markdown("### Step 2 — Dynamic Visual Pattern")

        st.markdown(
            '<div class="info-box"><b>Your enrolled logical pattern:</b> '
            f'{len(st.session_state.enrolled_pattern)} nodes<br>'
            '<b>Important:</b> The node numbers are randomly moved to new physical positions on every login.</div>',
            unsafe_allow_html=True,
        )

        mapping = st.session_state.physical_to_logical

        for row in range(3):
            cols = st.columns(3)
            for col_index in range(3):
                physical_index = row * 3 + col_index
                logical = mapping[physical_index]
                selected_pos = (
                    st.session_state.pattern_selected.index(logical) + 1
                    if logical in st.session_state.pattern_selected else None
                )
                label = (
                    f"✓ Node {logical} ({selected_pos})"
                    if selected_pos else f"● Node {logical}"
                )
                with cols[col_index]:
                    if st.button(
                        label,
                        key=f"login_node_{physical_index}_{logical}",
                        use_container_width=True,
                        disabled=logical in st.session_state.pattern_selected
                        or len(st.session_state.pattern_selected) >= len(st.session_state.enrolled_pattern),
                    ):
                        st.session_state.pattern_selected.append(logical)
                        st.session_state.pattern_error = ""
                        st.rerun()

        entered = st.session_state.pattern_selected
        st.markdown(
            f'<div class="info-box"><b>Pattern entered:</b> '
            f'{" → ".join(map(str, entered)) if entered else "None"}</div>',
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Clear Pattern", use_container_width=True):
                st.session_state.pattern_selected = []
                st.session_state.pattern_error = ""
                st.rerun()
        with b2:
            if st.button("Complete Secure Login", type="primary", use_container_width=True):
                if not st.session_state.otp_used:
                    st.error("Verify the OTP first.")
                elif entered != st.session_state.enrolled_pattern:
                    st.session_state.pattern_error = "Authentication failed."
                    if st.session_state.demo_mode:
                        st.error(
                            "Incorrect pattern for this demo. "
                            "Use the logical sequence you created during enrollment."
                        )
                    else:
                        st.error("Authentication failed. Please try again.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.page = "dashboard"
                    st.session_state.nav = "Home"
                    st.rerun()

        if st.session_state.pattern_error:
            st.error(st.session_state.pattern_error)

        st.markdown(
            '<div class="footer">Both OTP and the enrolled dynamic pattern are required.</div>',
            unsafe_allow_html=True,
        )

# ---------------- DASHBOARD ----------------
elif st.session_state.authenticated:
    nav_options = ["Home", "My Documents", "Issued Documents", "Shared Documents", "Profile", "Help", "Logout"]

    selected_nav = st.radio(
        "Navigation",
        nav_options,
        horizontal=True,
        index=nav_options.index(st.session_state.nav),
        label_visibility="collapsed",
    )

    if selected_nav != st.session_state.nav:
        st.session_state.nav = selected_nav
        if selected_nav == "Logout":
            logout()
            st.rerun()

    st.markdown(
        '<div class="dashboard-banner"><h1>Welcome back! 👋</h1>'
        '<p>Your documents are available in your Secure DigiLocker dashboard.</p></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.nav in ["Home", "My Documents"]:
        st.subheader("Your Documents")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Documents", "10")
        c2.metric("Verified", "7")
        c3.metric("Available", "10")

        st.markdown("### Important Documents")

        for start in range(0, len(DOCUMENTS), 2):
            cols = st.columns(2)
            for col, doc in zip(cols, DOCUMENTS[start:start + 2]):
                with col:
                    st.markdown(
                        f'<div class="dashboard-card">'
                        f'<div class="doc-icon">{doc["icon"]}</div>'
                        f'<div class="doc-name">{doc["name"]}</div>'
                        f'<div class="doc-meta"><b>Authority:</b> {doc["authority"]}</div>'
                        f'<div class="doc-meta"><b>Issue date:</b> {doc["date"]}</div>'
                        f'<span class="status">{doc["status"]}</span></div>',
                        unsafe_allow_html=True,
                    )
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View", key=f"view_{doc['name']}", use_container_width=True):
                            st.info(f"Demo view: {doc['name']}. This is a sample document.")
                    with b2:
                        sample = (
                            "SECURE DIGILOCKER ACADEMIC PROTOTYPE\n\n"
                            f"Document: {doc['name']}\n"
                            f"Issuing Authority: {doc['authority']}\n"
                            f"Status: {doc['status']}\n"
                            f"Issue Date: {doc['date']}\n\n"
                            "Dummy document for demonstration only."
                        )
                        st.download_button(
                            "Download",
                            data=sample,
                            file_name=f"{doc['name'].replace(' ', '_')}_sample.txt",
                            mime="text/plain",
                            key=f"download_{doc['name']}",
                            use_container_width=True,
                        )

    elif st.session_state.nav == "Issued Documents":
        st.subheader("Issued Documents")
        st.info("Sample issued documents only. No live government issuer is connected.")
        for doc in DOCUMENTS[:5]:
            st.write(f"{doc['icon']} **{doc['name']}** — {doc['authority']}")

    elif st.session_state.nav == "Shared Documents":
        st.subheader("Shared Documents")
        st.info("No sample documents have been shared yet.")

    elif st.session_state.nav == "Profile":
        st.subheader("Profile")
        st.write("**Account:** Demo User")
        st.write(f"**Mobile:** +91 {st.session_state.mobile}")
        st.write("**Authentication:** OTP + Dynamic Visual Pattern")
        st.write("**Account type:** Academic Prototype")

    elif st.session_state.nav == "Help":
        st.subheader("Help & Security Information")
        with st.expander("OTP security", expanded=True):
            st.write(
                "A cryptographically secure random OTP is generated. "
                "Only its HMAC-SHA256 digest is stored for verification. "
                "The OTP expires after 60 seconds and is invalid after successful use."
            )
        with st.expander("Dynamic pattern authentication"):
            st.write(
                "During enrollment, the user creates a logical sequence of nodes. "
                "During each login, those logical nodes are randomly shuffled across "
                "the physical 3x3 grid. The user selects the same logical sequence."
            )
        with st.expander("Combined authentication"):
            st.write(
                "Authentication requires both the correct OTP and the correct enrolled pattern."
            )
        with st.expander("Prototype limitation"):
            st.write(
                "This is an academic simulation. It does not connect to DigiLocker, UIDAI, "
                "SMS gateways, or government databases."
            )

    st.markdown(
        '<div class="footer">Secure DigiLocker | Academic Prototype | Dummy documents only</div>',
        unsafe_allow_html=True,
    )
