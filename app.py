import streamlit as st
import secrets
import hashlib
import hmac
import time
from datetime import datetime

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DEMO_PIN = "123456"
HMAC_SECRET = b"secure-digilocker-academic-demo-secret"

MAX_ATTEMPTS = 3
OTP_VALID_SECONDS = 60

# ---------------------------------------------------------
# SECURITY FUNCTIONS
# ---------------------------------------------------------

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
    if "otp_hash" not in st.session_state:
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


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "mobile_number": "",
    "stage": "mobile",

    "pin_attempts": 0,
    "pin_verified": False,

    "otp_hash": "",
    "otp_created_at": 0.0,
    "otp_attempts": 0,
    "otp_used": False,
    "otp_verified": False,

    "current_pattern": [],
    "entered_pattern": [],
    "pattern_attempts": 0,
    "pattern_verified": False,

    "login_status": False,

    "demo_otp": "",
    "font_scale": 1.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# RESET FUNCTIONS
# ---------------------------------------------------------

def restart_login():
    for key, value in defaults.items():
        st.session_state[key] = value
    st.rerun()


def logout():
    restart_login()


def create_new_otp():
    otp = generate_otp()

    st.session_state.demo_otp = otp
    st.session_state.otp_hash = otp_digest(otp)
    st.session_state.otp_created_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False
    st.session_state.stage = "otp"


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

scale = st.session_state.font_scale

st.markdown(
    f"""
    <style>

    .stApp {{
        background: #f5f1ff;
        font-size: {scale}em;
    }}

    .main-title {{
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }}

    .subtitle {{
        text-align: center;
        font-size: 16px;
        color: #555555;
        margin-bottom: 25px;
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
        margin-top: 10px;
        color: #4325a8;
    }}

    .brand-sub {{
        text-align: center;
        color: #666666;
        margin-bottom: 20px;
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

    .info-box {{
        background: #e9efff;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }}

    .pattern-display {{
        background: white;
        border: 2px solid #d8cef7;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        margin: 15px 0;
    }}

    .document-card {{
        background: white;
        border: 1px solid #ddd5ef;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
        min-height: 210px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}

    .document-title {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 12px;
    }}

    .document-info {{
        line-height: 1.8;
        color: #444444;
    }}

    .status {{
        font-weight: 700;
    }}

    .section-title {{
        font-size: 28px;
        font-weight: 700;
        margin: 20px 0;
    }}

    .success-box {{
        background: #e6f7ec;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #218739;
        margin: 15px 0;
    }}

    .warning-box {{
        background: #fff4d6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e0a800;
        margin: 15px 0;
    }}

    @media (max-width: 600px) {{

        .main-title {{
            font-size: 25px;
        }}

        .brand {{
            font-size: 25px;
        }}

        .gov-header {{
            font-size: 14px;
        }}

        .document-card {{
            min-height: auto;
        }}

        button {{
            min-height: 48px !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="gov-header">🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services</div>',
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


# ---------------------------------------------------------
# ACCESSIBILITY
# ---------------------------------------------------------

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
        '<div class="main-title">Login or Create Account</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Enter your mobile number to proceed</div>',
        unsafe_allow_html=True
    )

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

        if not mobile.isdigit() or len(mobile) != 10:
            st.error("Please enter a valid 10-digit mobile number.")

        elif mobile[0] not in "6789":
            st.error("Please enter a valid Indian mobile number.")

        else:

            st.session_state.mobile_number = mobile
            st.session_state.stage = "pin"
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
            "QR login is available as a future feature in this academic prototype."
        )

    st.info(
        "Academic Prototype: This application uses dummy data and "
        "does not connect to real DigiLocker services."
    )


# =========================================================
# SECURITY PIN
# =========================================================

elif st.session_state.stage == "pin":

    st.markdown(
        '<div class="main-title">Enter Security PIN</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Enter your 6-digit Security PIN to continue</div>',
        unsafe_allow_html=True
    )

    st.info("Demo Security PIN: 123456")

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

            st.error("Please enter a valid 6-digit Security PIN.")

        elif hmac.compare_digest(
            hash_pin(pin),
            hash_pin(DEMO_PIN)
        ):

            st.session_state.pin_verified = True
            create_new_otp()
            st.rerun()

        else:

            st.session_state.pin_attempts += 1

            remaining = MAX_ATTEMPTS - st.session_state.pin_attempts

            if remaining > 0:

                st.error("Incorrect Security PIN.")
                st.warning(
                    f"Remaining attempts: {remaining}"
                )

            else:

                st.error(
                    "Too many incorrect attempts. "
                    "Please restart authentication."
                )

                st.session_state.stage = "locked"

    if st.button("← Back", use_container_width=True):
        st.session_state.stage = "mobile"
        st.rerun()

    if st.button("Forgot Security PIN?", use_container_width=True):
        st.info(
            "Demo feature: In a real system, PIN recovery would "
            "use a secure account-recovery process."
        )

    st.caption(
        f"PIN attempts used: {st.session_state.pin_attempts}/{MAX_ATTEMPTS}"
    )


# =========================================================
# LOCKED
# =========================================================

elif st.session_state.stage == "locked":

    st.error(
        "Authentication has been temporarily stopped because "
        "too many incorrect Security PIN attempts were made."
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

    st.markdown(
        '<div class="main-title">OTP Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Verify your registered mobile number</div>',
        unsafe_allow_html=True
    )

    elapsed = int(time.time() - st.session_state.otp_created_at)
    remaining_seconds = max(
        0,
        OTP_VALID_SECONDS - elapsed
    )

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

        st.error("The OTP has expired.")

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

                st.error("This OTP has already been used.")

            elif not otp_input.isdigit() or len(otp_input) != 6:

                st.error("Please enter a valid 6-digit OTP.")

            elif verify_otp(otp_input):

                st.session_state.otp_used = True
                st.session_state.otp_verified = True

                # Generate a NEW pattern only after OTP success
                st.session_state.current_pattern = generate_pattern()
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

                    st.error("Incorrect OTP.")
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

    if st.button("← Back", use_container_width=True):
        st.session_state.stage = "pin"
        st.rerun()


# =========================================================
# DYNAMIC PATTERN
# =========================================================

elif st.session_state.stage == "pattern":

    st.markdown(
        '<div class="main-title">Dynamic Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Reproduce the pattern shown below</div>',
        unsafe_allow_html=True
    )

    # In DEMO MODE we show the pattern so the concept can be demonstrated.
    pattern_text = " → ".join(
        str(x) for x in st.session_state.current_pattern
    )

    st.markdown(
        f'<div class="pattern-display">{pattern_text}</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Tap the numbers in the same order as the pattern above."
    )

    st.write("### Number Grid")

    # -----------------------------------------------------
    # 3 x 3 NUMBER GRID
    # -----------------------------------------------------

    for row in range(3):

        cols = st.columns(3)

        for col in range(3):

            number = row * 3 + col + 1

            with cols[col]:

                if number in st.session_state.entered_pattern:
                    label = f"✓ {number}"
                else:
                    label = str(number)

                if st.button(
                    label,
                    key=f"pattern_{number}",
                    use_container_width=True
                ):

                    if number not in st.session_state.entered_pattern:

                        st.session_state.entered_pattern.append(
                            number
                        )

                        st.rerun()

    entered_text = " → ".join(
        str(x)
        for x in st.session_state.entered_pattern
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

            if (
                st.session_state.entered_pattern ==
                st.session_state.current_pattern
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

                    st.error("Incorrect pattern.")
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
        '<div class="main-title">Welcome back!</div>',
        unsafe_allow_html=True
    )

    st.success(
        "All authentication factors verified successfully."
    )

    st.write(
        "### Secure DigiLocker Dashboard"
    )

    # -----------------------------------------------------
    # USER SUMMARY
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Documents", "10")

    with col2:
        st.metric("Verified", "10")

    with col3:
        st.metric("Shared", "2")

    st.divider()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

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

        st.markdown(
            '<div class="section-title">Important Documents</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Access your important digital documents from one place."
        )

    elif nav == "My Documents":

        st.markdown(
            '<div class="section-title">My Documents</div>',
            unsafe_allow_html=True
        )

    elif nav == "Issued Documents":

        st.markdown(
            '<div class="section-title">Issued Documents</div>',
            unsafe_allow_html=True
        )

        st.info(
            "These are sample documents for the academic prototype."
        )

    elif nav == "Shared Documents":

        st.markdown(
            '<div class="section-title">Shared Documents</div>',
            unsafe_allow_html=True
        )

        st.info(
            "No real documents are shared. This is demo data."
        )

    elif nav == "Profile":

        st.markdown(
            '<div class="section-title">Profile</div>',
            unsafe_allow_html=True
        )

        st.write("Mobile Number: ******" + st.session_state.mobile_number[-4:])
        st.write("Account Type: Academic Demo Account")
        st.write("Authentication: PIN + OTP + Dynamic Pattern")

    elif nav == "Help":

        st.markdown(
            '<div class="section-title">Help</div>',
            unsafe_allow_html=True
        )

        st.write(
            "This application is an academic prototype demonstrating "
            "multi-factor authentication."
        )

    st.divider()

    # -----------------------------------------------------
    # DOCUMENT DATA
    # -----------------------------------------------------

    documents = [
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

    st.markdown(
        '<div class="section-title">Important Documents</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DOCUMENT CARDS
    # -----------------------------------------------------

    for i in range(0, len(documents), 2):

        cols = st.columns(2)

        for j in range(2):

            index = i + j

            if index >= len(documents):
                continue

            doc = documents[index]

            with cols[j]:

                st.markdown(
                    f"""
                    <div class="document-card">
                        <div class="document-title">
                            {doc["name"]}
                        </div>

                        <div class="document-info">
                            <b>Issuing Authority:</b>
                            {doc["authority"]}<br>

                            <b>Status:</b>
                            <span class="status">
                                ✓ {doc["status"]}
                            </span><br>

                            <b>Issue Date:</b>
                            {doc["date"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                b1, b2 = st.columns(2)

                with b1:

                    if st.button(
                        "View",
                        key=f"view_{index}",
                        use_container_width=True
                    ):
                        st.info(
                            f"Viewing sample document: {doc['name']}"
                        )

                with b2:

                    if st.button(
                        "Download",
                        key=f"download_{index}",
                        use_container_width=True
                    ):
                        st.success(
                            "Demo download selected. "
                            "No real document is downloaded."
                        )

    st.divider()

    # -----------------------------------------------------
    # SECURITY INFORMATION
    # -----------------------------------------------------

    with st.expander("🔐 Academic Prototype / Security Explanation"):

        st.write("### Security PIN")
        st.write(
            "The Security PIN acts as the primary authentication factor."
        )

        st.write("### OTP")
        st.write(
            "The OTP demonstrates verification of possession "
            "of the registered mobile number."
        )

        st.write("### Dynamic Pattern")
        st.write(
            "After successful OTP verification, a new random "
            "3–5 number pattern is generated for the authentication session."
        )

        st.write("### Security Controls")

        st.write(
            "• Security PIN: maximum 3 attempts"
        )

        st.write(
            "• OTP: 60-second expiry"
        )

        st.write(
            "• OTP: maximum 3 incorrect attempts"
        )

        st.write(
            "• OTP: invalidated after successful verification"
        )

        st.write(
            "• Pattern: maximum 3 attempts"
        )

        st.write(
            "• Pattern: generated only after successful OTP verification"
        )

        st.write(
            "• Combined authentication: PIN + OTP + Pattern"
        )

    if st.button(
        "🚪 Logout",
        type="primary",
        use_container_width=True
    ):
        logout()
