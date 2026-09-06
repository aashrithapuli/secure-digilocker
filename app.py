import streamlit as st
import secrets
import hashlib
import hmac
import time

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

MAX_ATTEMPTS = 3
OTP_VALID_SECONDS = 60


# =========================================================
# DOCUMENT DATA
# =========================================================

DOCUMENTS = [
    {
        "name": "🪪 Aadhaar Card",
        "authority": "UIDAI",
        "status": "Verified",
        "date": "15 Jan 2025"
    },
    {
        "name": "🚗 Driving Licence",
        "authority": "Transport Department",
        "status": "Verified",
        "date": "20 Feb 2025"
    },
    {
        "name": "🗳️ Voter ID",
        "authority": "Election Commission",
        "status": "Verified",
        "date": "10 Mar 2025"
    },
    {
        "name": "🎓 Class 10 Certificate",
        "authority": "Education Board",
        "status": "Verified",
        "date": "05 Apr 2025"
    },
    {
        "name": "🎓 Class 12 Certificate",
        "authority": "Education Board",
        "status": "Verified",
        "date": "12 May 2025"
    },
    {
        "name": "🎓 Degree Certificate",
        "authority": "University",
        "status": "Verified",
        "date": "15 Jun 2025"
    },
    {
        "name": "📄 PAN Card",
        "authority": "Income Tax Department",
        "status": "Verified",
        "date": "18 Jul 2025"
    },
    {
        "name": "🏥 Health Certificate",
        "authority": "Health Department",
        "status": "Verified",
        "date": "22 Aug 2025"
    },
    {
        "name": "🏦 Income Certificate",
        "authority": "Revenue Department",
        "status": "Verified",
        "date": "30 Sep 2025"
    },
    {
        "name": "📑 Other Documents",
        "authority": "Various Authorities",
        "status": "Available",
        "date": "01 Oct 2025"
    }
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

    "current_pattern": [],
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
# SECURITY FUNCTIONS
# =========================================================

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def otp_digest(otp):
    return hmac.new(
        HMAC_SECRET,
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_otp(otp):
    if not st.session_state.otp_hash:
        return False

    return hmac.compare_digest(
        otp_digest(otp),
        st.session_state.otp_hash
    )


def generate_pattern():
    length = secrets.choice([3, 4, 5])

    return secrets.SystemRandom().sample(
        list(range(1, 10)),
        length
    )


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

    st.session_state.current_pattern = []
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

    st.session_state.current_pattern = []
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False

    st.session_state.login_status = False

    st.session_state.stage = "pin"


def restart_login():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()


def logout():
    restart_login()


def otp_remaining():
    if not st.session_state.otp_created_at:
        return 0

    elapsed = int(
        time.time() - st.session_state.otp_created_at
    )

    return max(
        0,
        OTP_VALID_SECONDS - elapsed
    )


# =========================================================
# CSS
# =========================================================

scale = st.session_state.font_scale

st.markdown(
    f"""
    <style>

    .stApp {{
        background: #f5f1ff;
        font-size: {scale}em;
    }}

    .block-container {{
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }}

    .gov-header {{
        background: #10246b;
        color: white;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
    }}

    .brand {{
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        color: #4325a8;
        margin-top: 10px;
    }}

    .brand-sub {{
        text-align: center;
        color: #666666;
        margin-bottom: 15px;
    }}

    .prototype {{
        display: inline-block;
        background: #eee8ff;
        color: #4325a8;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 8px;
    }}

    .login-card {{
        background: white;
        border: 1px solid #ddd5ef;
        border-radius: 18px;
        padding: 28px;
        margin: 25px auto;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    }}

    .login-title {{
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        color: #111111;
    }}

    .login-subtitle {{
        text-align: center;
        color: #666666;
        margin-top: 5px;
        margin-bottom: 15px;
    }}

    .info-box {{
        background: #e9efff;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }}

    .pattern-box {{
        background: white;
        border: 2px solid #d8cef7;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }}

    .pattern-number {{
        font-size: 30px;
        font-weight: 800;
        color: #4325a8;
        letter-spacing: 5px;
    }}

    .section-title {{
        font-size: 28px;
        font-weight: 700;
        margin: 20px 0;
    }}

    .dashboard-banner {{
        background: linear-gradient(135deg, #5634dd, #7d5bea);
        color: white;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 22px;
    }}

    .dashboard-banner h1 {{
        margin: 0;
        font-size: 30px;
    }}

    .document-card {{
        background: white;
        border: 1px solid #ddd5ef;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 10px;
        min-height: 210px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}

    .document-title {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 15px;
    }}

    .document-info {{
        line-height: 1.8;
        color: #444444;
    }}

    .status {{
        display: inline-block;
        padding: 5px 10px;
        border-radius: 12px;
        background: #e6f7ec;
        color: #176b2c;
        font-weight: 700;
        margin-top: 5px;
    }}

    .footer {{
        text-align: center;
        color: #666666;
        padding: 25px 10px;
        font-size: 13px;
    }}

    @media (max-width: 600px) {{

        .block-container {{
            padding-left: 12px;
            padding-right: 12px;
        }}

        .gov-header {{
            font-size: 13px;
            padding: 12px 8px;
        }}

        .brand {{
            font-size: 24px;
        }}

        .login-card {{
            padding: 20px 15px;
            margin: 15px 0;
        }}

        .login-title {{
            font-size: 25px;
        }}

        .section-title {{
            font-size: 23px;
        }}

        .dashboard-banner {{
            padding: 20px;
        }}

        .dashboard-banner h1 {{
            font-size: 24px;
        }}

        .document-card {{
            min-height: auto;
        }}

        button {{
            min-height: 48px !important;
        }}

        input {{
            min-height: 48px !important;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="gov-header">🇮🇳 Government of India | Secure Digital Services</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand">🔐 Secure DigiLocker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;"><span class="prototype">ACADEMIC PROTOTYPE</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand-sub">Secure digital document access</div>',
    unsafe_allow_html=True
)


# =========================================================
# ACCESSIBILITY
# =========================================================

with st.expander("♿ Accessibility"):

    st.write("Adjust text size:")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("A−", use_container_width=True):
            st.session_state.font_scale = max(
                0.8,
                st.session_state.font_scale - 0.1
            )
            st.rerun()

    with c2:
        if st.button("A", use_container_width=True):
            st.session_state.font_scale = 1.0
            st.rerun()

    with c3:
        if st.button("A+", use_container_width=True):
            st.session_state.font_scale = min(
                1.5,
                st.session_state.font_scale + 0.1
            )
            st.rerun()


# =========================================================
# MOBILE NUMBER
# =========================================================

if st.session_state.stage == "mobile":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">Login or Create Account</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Enter your mobile number to proceed</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    mobile = st.text_input(
        "Mobile Number",
        placeholder="10-digit mobile number",
        max_chars=10
    )

    st.caption("🇮🇳 +91 India")

    if st.button(
        "Continue",
        type="primary",
        use_container_width=True
    ):

        cleaned = mobile.strip().replace(" ", "")

        if not cleaned.isdigit() or len(cleaned) != 10:

            st.error(
                "Please enter a valid 10-digit mobile number."
            )

        elif cleaned[0] not in "6789":

            st.error(
                "Please enter a valid Indian mobile number."
            )

        else:

            start_authentication(cleaned)
            st.rerun()

    st.caption(
        "By continuing, I agree to the Terms of Service."
    )

    st.divider()

    if st.button(
        "📱 Login using QR Code",
        use_container_width=True
    ):

        st.info(
            "QR login is simulated for this academic prototype."
        )

    st.info(
        "Academic Prototype: This application uses dummy data "
        "and does not connect to real DigiLocker services."
    )


# =========================================================
# SECURITY PIN
# =========================================================

elif st.session_state.stage == "pin":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">Enter Security PIN</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Enter your 6-digit Security PIN to continue</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Demo Security PIN: 123456"
    )

    pin = st.text_input(
        "Security PIN",
        type="password",
        max_chars=6,
        placeholder="Enter 6-digit PIN"
    )

    if st.button(
        "Continue",
        type="primary",
        use_container_width=True
    ):

        if not pin.isdigit() or len(pin) != 6:

            st.error(
                "Please enter a valid 6-digit Security PIN."
            )

        elif hmac.compare_digest(
            hash_pin(pin),
            hash_pin(DEMO_PIN)
        ):

            st.session_state.pin_verified = True

            create_new_otp()

            st.rerun()

        else:

            st.session_state.pin_attempts += 1

            remaining = (
                MAX_ATTEMPTS -
                st.session_state.pin_attempts
            )

            if remaining > 0:

                st.error(
                    "Incorrect Security PIN."
                )

                st.warning(
                    f"Remaining attempts: {remaining}"
                )

            else:

                st.error(
                    "Too many incorrect attempts. "
                    "Please restart authentication."
                )

                st.session_state.stage = "locked"

    if st.button(
        "← Back",
        use_container_width=True
    ):

        st.session_state.stage = "mobile"
        st.rerun()

    if st.button(
        "Forgot Security PIN?",
        use_container_width=True
    ):

        st.info(
            "Demo feature: In a real system, PIN recovery "
            "would use a secure account-recovery process."
        )

    st.caption(
        f"PIN attempts: "
        f"{st.session_state.pin_attempts}/{MAX_ATTEMPTS}"
    )


# =========================================================
# ACCOUNT LOCKED
# =========================================================

elif st.session_state.stage == "locked":

    st.error(
        "Authentication has been temporarily stopped "
        "because too many incorrect Security PIN attempts "
        "were made."
    )

    st.warning(
        "Please restart the authentication process."
    )

    if st.button(
        "Restart Login",
        type="primary",
        use_container_width=True
    ):

        restart_login()


# =========================================================
# OTP
# =========================================================

elif st.session_state.stage == "otp":

    if st_autorefresh is not None:

        st_autorefresh(
            interval=1000,
            key="otp_timer"
        )

    remaining_seconds = otp_remaining()

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">OTP Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Verify your registered mobile number</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Demo OTP — In a real system this would be sent through SMS."
    )

    st.success(
        f"Demo OTP: {st.session_state.demo_otp}"
    )

    st.metric(
        "OTP Valid For",
        f"{remaining_seconds} seconds"
    )

    if remaining_seconds <= 0:

        st.error(
            "The OTP has expired."
        )

        if st.button(
            "Resend OTP",
            type="primary",
            use_container_width=True
        ):

            create_new_otp()
            st.rerun()

    else:

        otp_input = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            placeholder="Enter OTP",
            type="password"
        )

        if st.button(
            "Verify OTP",
            type="primary",
            use_container_width=True
        ):

            if st.session_state.otp_used:

                st.error(
                    "This OTP has already been used."
                )

            elif not otp_input.isdigit() or len(otp_input) != 6:

                st.error(
                    "Please enter a valid 6-digit OTP."
                )

            elif remaining_seconds <= 0:

                st.error(
                    "The OTP has expired. Please request a new OTP."
                )

            elif st.session_state.otp_attempts >= MAX_ATTEMPTS:

                st.error(
                    "Too many incorrect OTP attempts. "
                    "Please request a new OTP."
                )

            elif verify_otp(otp_input):

                st.session_state.otp_used = True
                st.session_state.otp_verified = True

                st.session_state.current_pattern = (
                    generate_pattern()
                )

                st.session_state.entered_pattern = []
                st.session_state.pattern_attempts = 0

                st.session_state.stage = "pattern"

                st.rerun()

            else:

                st.session_state.otp_attempts += 1

                remaining = (
                    MAX_ATTEMPTS -
                    st.session_state.otp_attempts
                )

                if remaining > 0:

                    st.error(
                        "Incorrect OTP."
                    )

                    st.warning(
                        f"Remaining attempts: {remaining}"
                    )

                else:

                    st.error(
                        "Too many incorrect OTP attempts. "
                        "Please request a new OTP."
                    )

        if st.button(
            "Resend OTP",
            use_container_width=True
        ):

            create_new_otp()
            st.rerun()

    if st.button(
        "← Back",
        use_container_width=True
    ):

        st.session_state.stage = "pin"
        st.rerun()


# =========================================================
# DYNAMIC PATTERN
# =========================================================

elif st.session_state.stage == "pattern":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">Dynamic Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Remember the pattern and reproduce it below</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    pattern_text = " → ".join(
        str(number)
        for number in st.session_state.current_pattern
    )

    st.markdown(
        '<div class="pattern-box">',
        unsafe_allow_html=True
    )

    st.write("### Pattern")

    st.markdown(
        f'<div class="pattern-number">{pattern_text}</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Remember the numbers in the order shown above, "
        "then select them in the same order."
    )

    st.subheader("Number Grid")

    for row in range(3):

        cols = st.columns(3)

        for col in range(3):

            number = row * 3 + col + 1

            with cols[col]:

                if number in st.session_state.entered_pattern:

                    position = (
                        st.session_state.entered_pattern.index(number)
                        + 1
                    )

                    button_label = (
                        f"✓ {number}  ({position})"
                    )

                else:

                    button_label = str(number)

                if st.button(
                    button_label,
                    key=f"pattern_button_{number}",
                    use_container_width=True
                ):

                    if number not in st.session_state.entered_pattern:

                        if len(
                            st.session_state.entered_pattern
                        ) < len(
                            st.session_state.current_pattern
                        ):

                            st.session_state.entered_pattern.append(
                                number
                            )

                            st.rerun()

    entered_text = " → ".join(
        str(number)
        for number in st.session_state.entered_pattern
    )

    if entered_text:

        st.write(
            f"**Pattern entered:** {entered_text}"
        )

    else:

        st.write(
            "**Pattern entered:** —"
        )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Clear Pattern",
            use_container_width=True
        ):

            st.session_state.entered_pattern = []
            st.rerun()

    with c2:

        if st.button(
            "Verify Pattern",
            type="primary",
            use_container_width=True
        ):

            if not st.session_state.otp_verified:

                st.error(
                    "OTP verification is required first."
                )

            elif st.session_state.otp_used is not True:

                st.error(
                    "OTP verification is required first."
                )

            elif (
                st.session_state.entered_pattern
                == st.session_state.current_pattern
            ):

                st.session_state.pattern_verified = True
                st.session_state.login_status = True
                st.session_state.stage = "dashboard"

                st.rerun()

            else:

                st.session_state.pattern_attempts += 1

                remaining = (
                    MAX_ATTEMPTS -
                    st.session_state.pattern_attempts
                )

                st.session_state.entered_pattern = []

                if remaining > 0:

                    st.error(
                        "Incorrect pattern."
                    )

                    st.warning(
                        f"Remaining attempts: {remaining}"
                    )

                    st.rerun()

                else:

                    st.session_state.stage = "pattern_failed"
                    st.rerun()

    st.caption(
        f"Pattern attempts: "
        f"{st.session_state.pattern_attempts}/{MAX_ATTEMPTS}"
    )


# =========================================================
# PATTERN FAILED
# =========================================================

elif st.session_state.stage == "pattern_failed":

    st.error(
        "Pattern authentication failed. "
        "Please restart login."
    )

    if st.button(
        "Restart Login",
        type="primary",
        use_container_width=True
    ):

        restart_login()


# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state.stage == "dashboard":

    st.markdown(
        '<div class="dashboard-banner">',
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1>Welcome back! 👋</h1>",
        unsafe_allow_html=True
    )

    st.write(
        "Your secure digital documents are available below."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.success(
        "All authentication factors verified successfully."
    )

    if st.button(
        "🚪 Logout",
        type="primary",
        use_container_width=True
    ):

        logout()

    st.subheader("Secure DigiLocker Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Documents",
            "10"
        )

    with col2:
        st.metric(
            "Verified",
            "10"
        )

    with col3:
        st.metric(
            "Shared",
            "2"
        )

    st.divider()

    nav = st.selectbox(
        "Navigation",
        [
            "Home",
            "My Documents",
            "Issued Documents",
            "Shared Documents",
            "Profile",
            "Help"
        ]
    )

    if nav == "Home":

        st.subheader("Important Documents")

        st.write(
            "Access your important digital documents from one place."
        )

    elif nav == "My Documents":

        st.subheader("My Documents")

    elif nav == "Issued Documents":

        st.subheader("Issued Documents")

        st.info(
            "These are sample documents for the academic prototype."
        )

    elif nav == "Shared Documents":

        st.subheader("Shared Documents")

        st.info(
            "No real documents are shared. This is demo data."
        )

    elif nav == "Profile":

        st.subheader("Profile")

        st.write(
            "Account: Demo User"
        )

        st.write(
            "Mobile Number: ******"
            + st.session_state.mobile_number[-4:]
        )

        st.write(
            "Authentication: PIN + OTP + Dynamic Pattern"
        )

        st.write(
            "Account Type: Academic Prototype"
        )

    elif nav == "Help":

        st.subheader(
            "Help & Security Information"
        )

        with st.expander(
            "Security PIN"
        ):

            st.write(
                "The Security PIN acts as the primary authentication factor."
            )

        with st.expander(
            "OTP Security"
        ):

            st.write(
                "A cryptographically secure random 6-digit OTP "
                "is generated."
            )

            st.write(
                "Only an HMAC-SHA256 representation is stored "
                "for verification."
            )

            st.write(
                "The OTP expires after 60 seconds and becomes "
                "invalid after successful use."
            )

        with st.expander(
            "Dynamic Pattern"
        ):

            st.write(
                "A new 3–5 number pattern is generated only "
                "after successful OTP verification."
            )

            st.write(
                "The user must reproduce the generated sequence "
                "using the numbered 3×3 grid."
            )

        with st.expander(
            "Combined Authentication"
        ):

            st.write(
                "Authentication requires the correct Security PIN, "
                "OTP and Dynamic Pattern."
            )

        with st.expander(
            "Prototype Limitation"
        ):

            st.write(
                "This is an academic simulation. It does not connect "
                "to DigiLocker, UIDAI, SMS gateways or government databases."
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

                    st.markdown(
                        f"### {doc['name']}"
                    )

                    st.write(
                        f"**Issuing Authority:** "
                        f"{doc['authority']}"
                    )

                    st.write(
                        f"**Issue Date:** "
                        f"{doc['date']}"
                    )

                    if doc["status"] == "Verified":

                        st.success(
                            "✓ Verified"
                        )

                    else:

                        st.info(
                            doc["status"]
                        )

                    b1, b2 = st.columns(2)

                    with b1:

                        if st.button(
                            "View",
                            key=f"view_{index}",
                            use_container_width=True
                        ):

                            st.info(
                                f"Viewing sample document: "
                                f"{doc['name']}"
                            )

                    with b2:

                        sample_document = (
                            "SECURE DIGILOCKER "
                            "ACADEMIC PROTOTYPE\n\n"
                            f"Document: {doc['name']}\n"
                            f"Issuing Authority: {doc['authority']}\n"
                            f"Status: {doc['status']}\n"
                            f"Issue Date: {doc['date']}\n\n"
                            "Dummy document for demonstration only."
                        )

                        st.download_button(
                            "Download",
                            data=sample_document,
                            file_name=(
                                doc["name"]
                                .replace("🪪 ", "")
                                .replace("🚗 ", "")
                                .replace("🗳️ ", "")
                                .replace("🎓 ", "")
                                .replace("📄 ", "")
                                .replace("🏥 ", "")
                                .replace("🏦 ", "")
                                .replace("📑 ", "")
                                .replace(" ", "_")
                                + "_sample.txt"
                            ),
                            mime="text/plain",
                            key=f"download_{index}",
                            use_container_width=True
                        )

    st.divider()

    with st.expander(
        "🔐 Academic Prototype / Security Explanation"
    ):

        st.subheader("Security PIN")

        st.write(
            "Primary authentication factor. "
            "The prototype allows a maximum of three incorrect attempts."
        )

        st.subheader("OTP")

        st.write(
            "A cryptographically secure six-digit OTP is generated "
            "after successful Security PIN verification."
        )

        st.write(
            "The OTP is valid for 60 seconds."
        )

        st.write(
            "After three incorrect attempts, a new OTP must be requested."
        )

        st.write(
            "The OTP is invalidated after successful verification."
        )

        st.subheader("Dynamic Pattern")

        st.write(
            "After successful OTP verification, a new random pattern "
            "containing three to five unique numbers from 1 to 9 is generated."
        )

        st.write(
            "The user must reproduce the numbers in the same order."
        )

        st.subheader("Final Authentication")

        st.write(
            "Security PIN + OTP + Dynamic Pattern = "
            "Multi-factor authentication prototype."
        )

    st.markdown(
        '<div class="footer">'
        'Secure DigiLocker | Academic Prototype | Dummy documents only'
        '</div>',
        unsafe_allow_html=True
    )
