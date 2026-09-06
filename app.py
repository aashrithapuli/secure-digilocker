import streamlit as st
import secrets
import hashlib
import hmac
import time
from datetime import datetime


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------

defaults = {
    "mobile_number": "",
    "authentication_stage": "mobile",
    "security_pin_attempts": 0,
    "security_pin_verified": False,
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
    "show_pin": False,
    "font_size": 16,
    "session_id": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

DEMO_PIN = "123456"
PIN_HASH = hashlib.sha256(DEMO_PIN.encode()).hexdigest()

# Academic-demo secret.
# Production systems should keep this in a secure secret manager.
HMAC_SECRET = b"secure-digilocker-academic-demo-secret"


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
        "date": "12 Apr 2024"
    },
    {
        "name": "🎓 Class 12 Certificate",
        "authority": "Education Board",
        "status": "Verified",
        "date": "18 May 2024"
    },
    {
        "name": "🎓 Degree Certificate",
        "authority": "University",
        "status": "Verified",
        "date": "25 Jun 2025"
    },
    {
        "name": "📄 PAN Card",
        "authority": "Income Tax Department",
        "status": "Verified",
        "date": "05 Jul 2024"
    },
    {
        "name": "🏥 Health Certificate",
        "authority": "Health Department",
        "status": "Verified",
        "date": "08 Aug 2025"
    },
    {
        "name": "🏦 Income Certificate",
        "authority": "Revenue Department",
        "status": "Verified",
        "date": "14 Sep 2025"
    },
    {
        "name": "📑 Other Documents",
        "authority": "Government Services",
        "status": "Available",
        "date": "01 Oct 2025"
    }
]


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

font_size = st.session_state.font_size

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #f5f1ff;
        font-size: {font_size}px;
    }}

    .gov-header {{
        background-color: #10246b;
        color: white;
        padding: 14px 20px;
        font-weight: 600;
        font-size: 15px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 20px;
    }}

    .brand {{
        background: white;
        padding: 20px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }}

    .brand-name {{
        font-size: 28px;
        font-weight: 700;
        color: #4f2db8;
    }}

    .brand-sub {{
        color: #666;
        margin-top: 5px;
    }}

    .badge {{
        display: inline-block;
        background: #eee8ff;
        color: #4f2db8;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: 700;
        margin-left: 8px;
    }}

    .login-card {{
        background: white;
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 5px 25px rgba(50, 30, 100, 0.10);
        margin-bottom: 20px;
    }}

    .page-title {{
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }}

    .subtitle {{
        color: #667085;
        margin-bottom: 20px;
    }}

    .demo-box {{
        background: #fff8df;
        border-left: 5px solid #e0a800;
        padding: 14px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    .security-box {{
        background: #eef4ff;
        border-left: 5px solid #3867d6;
        padding: 14px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    .document-card {{
        background: white;
        border: 1px solid #ddd;
        border-radius: 14px;
        padding: 20px;
        min-height: 170px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }}

    .document-title {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    .document-info {{
        color: #555;
        line-height: 1.7;
    }}

    .pattern-display {{
        background: #eee9ff;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        color: #4f2db8;
        margin: 15px 0;
    }}

    .pattern-grid {{
        max-width: 420px;
        margin: auto;
    }}

    .footer {{
        text-align: center;
        color: #777;
        font-size: 13px;
        padding: 25px 0;
    }}

    button {{
        min-height: 46px !important;
    }}

    @media (max-width: 600px) {{
        .login-card {{
            padding: 20px;
        }}

        .page-title {{
            font-size: 24px;
        }}

        .brand-name {{
            font-size: 23px;
        }}

        .pattern-grid {{
            width: 100%;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def hash_otp(otp):
    return hmac.new(
        HMAC_SECRET,
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_pattern():
    length = secrets.choice([3, 4, 5])
    return secrets.SystemRandom().sample(
        list(range(1, 10)),
        length
    )


def reset_authentication():
    st.session_state.mobile_number = ""
    st.session_state.authentication_stage = "mobile"
    st.session_state.security_pin_attempts = 0
    st.session_state.security_pin_verified = False
    st.session_state.otp_hash = ""
    st.session_state.otp_created_at = 0.0
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.otp_verified = False
    st.session_state.current_pattern = []
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False
    st.session_state.login_status = False
    st.session_state.demo_otp = ""
    st.session_state.show_pin = False
    st.session_state.session_id = secrets.token_hex(8)


def generate_new_otp():
    otp = generate_otp()

    st.session_state.demo_otp = otp
    st.session_state.otp_hash = hash_otp(otp)
    st.session_state.otp_created_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False


def otp_expired():
    if st.session_state.otp_created_at == 0:
        return True

    return time.time() - st.session_state.otp_created_at >= 60


def otp_remaining_seconds():
    if st.session_state.otp_created_at == 0:
        return 0

    remaining = 60 - int(time.time() - st.session_state.otp_created_at)

    return max(0, remaining)


def generate_dynamic_pattern():
    st.session_state.current_pattern = generate_pattern()
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.pattern_verified = False


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="gov-header">
        🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services
    </div>

    <div class="brand">
        <div class="brand-name">
            🔐 Secure DigiLocker
            <span class="badge">ACADEMIC PROTOTYPE</span>
        </div>
        <div class="brand-sub">
            Secure digital document access
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# ACCESSIBILITY CONTROLS
# ---------------------------------------------------------

with st.expander("♿ Accessibility Settings"):
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("A−", use_container_width=True):
            st.session_state.font_size = max(
                14,
                st.session_state.font_size - 1
            )
            st.rerun()

    with col2:
        st.write(
            f"Text size: {st.session_state.font_size}px"
        )

    with col3:
        if st.button("A+", use_container_width=True):
            st.session_state.font_size = min(
                24,
                st.session_state.font_size + 1
            )
            st.rerun()


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if st.session_state.login_status:

    st.title("Welcome back! 👋")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("My Documents")

    with col2:
        if st.button("Logout", use_container_width=True):
            reset_authentication()
            st.rerun()

    st.success("Authentication completed successfully.")

    st.info(
        "You have successfully completed Security PIN + OTP + "
        "Dynamic Pattern authentication."
    )

    st.write("### Document Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Documents", len(DOCUMENTS))

    with c2:
        st.metric("Verified", 9)

    with c3:
        st.metric("Available", 10)

    st.divider()

    st.subheader("Important Documents")

    for i in range(0, len(DOCUMENTS), 2):

        cols = st.columns(2)

        for j in range(2):

            index = i + j

            if index < len(DOCUMENTS):

                document = DOCUMENTS[index]

                with cols[j]:

                    st.markdown(
                        f"""
                        <div class="document-card">
                            <div class="document-title">
                                {document["name"]}
                            </div>

                            <div class="document-info">
                                <b>Issuing Authority:</b>
                                {document["authority"]}<br>

                                <b>Status:</b>
                                {document["status"]}<br>

                                <b>Issue Date:</b>
                                {document["date"]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    view_col, download_col = st.columns(2)

                    with view_col:
                        if st.button(
                            "View",
                            key=f"view_{index}",
                            use_container_width=True
                        ):
                            st.info(
                                f"Demo preview: {document['name']}"
                            )

                    with download_col:
                        demo_file = (
                            f"Secure DigiLocker Demo Document\n\n"
                            f"Document: {document['name']}\n"
                            f"Issuing Authority: {document['authority']}\n"
                            f"Status: {document['status']}\n"
                            f"Issue Date: {document['date']}\n\n"
                            f"This is a dummy academic prototype document."
                        )

                        st.download_button(
                            "Download",
                            data=demo_file,
                            file_name=f"demo_document_{index + 1}.txt",
                            mime="text/plain",
                            key=f"download_{index}",
                            use_container_width=True
                        )

    st.divider()

    st.subheader("Services")

    service_cols = st.columns(4)

    with service_cols[0]:
        st.button(
            "📁 My Documents",
            use_container_width=True
        )

    with service_cols[1]:
        st.button(
            "📤 Issued Documents",
            use_container_width=True
        )

    with service_cols[2]:
        st.button(
            "🔗 Shared Documents",
            use_container_width=True
        )

    with service_cols[3]:
        st.button(
            "❓ Help",
            use_container_width=True
        )

    st.markdown(
        """
        <div class="footer">
            Secure DigiLocker — Academic Prototype<br>
            This application uses dummy documents for demonstration only.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ---------------------------------------------------------
# MOBILE NUMBER SCREEN
# ---------------------------------------------------------

if st.session_state.authentication_stage == "mobile":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-title">Login or Create Account</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Enter your mobile number to proceed</div>',
        unsafe_allow_html=True
    )

    mobile = st.text_input(
        "Mobile number",
        placeholder="10-digit mobile number",
        max_chars=10
    )

    st.markdown(
        """
        <div class="security-box">
            🔐 Your mobile number is used only for this academic prototype.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Continue",
        type="primary",
        use_container_width=True
    ):

        if (
            len(mobile) != 10
            or not mobile.isdigit()
            or mobile[0] not in "6789"
        ):
            st.error(
                "Please enter a valid 10-digit Indian mobile number."
            )
        else:
            st.session_state.mobile_number = mobile
            st.session_state.authentication_stage = "pin"
            st.session_state.security_pin_attempts = 0
            st.session_state.session_id = secrets.token_hex(8)
            st.rerun()

    st.markdown(
        """
        <div class="footer">
            By continuing, I agree to the Terms of Service.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECURITY PIN SCREEN
# ---------------------------------------------------------

elif st.session_state.authentication_stage == "pin":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-title">Enter Security PIN</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Enter your 6-digit Security PIN to continue'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="demo-box">
            <b>Academic Demo</b><br>
            Demo Security PIN: <b>123456</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    show_pin = st.checkbox("Show PIN")

    pin_type = "default" if show_pin else "password"

    pin = st.text_input(
        "Security PIN",
        type=pin_type,
        max_chars=6,
        placeholder="Enter 6-digit PIN"
    )

    if st.button(
        "Continue",
        type="primary",
        use_container_width=True
    ):

        if len(pin) != 6 or not pin.isdigit():
            st.error("Security PIN must contain exactly 6 digits.")

        else:

            entered_hash = hash_pin(pin)

            if hmac.compare_digest(entered_hash, PIN_HASH):

                st.session_state.security_pin_verified = True
                st.session_state.authentication_stage = "otp"

                generate_new_otp()

                st.rerun()

            else:

                st.session_state.security_pin_attempts += 1

                remaining = (
                    3 -
                    st.session_state.security_pin_attempts
                )

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

                    if st.button(
                        "Restart Login",
                        use_container_width=True
                    ):
                        reset_authentication()
                        st.rerun()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Back",
            use_container_width=True
        ):

            st.session_state.authentication_stage = "mobile"
            st.session_state.security_pin_attempts = 0
            st.rerun()

    with col2:

        if st.button(
            "Forgot Security PIN?",
            use_container_width=True
        ):

            st.info(
                "For this academic prototype, use the "
                "Demo Security PIN: 123456"
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# OTP SCREEN
# ---------------------------------------------------------

elif st.session_state.authentication_stage == "otp":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-title">OTP Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Verify the OTP generated for your registered mobile number'
        '</div>',
        unsafe_allow_html=True
    )

    remaining = otp_remaining_seconds()

    if remaining > 0:

        st.info(
            f"OTP expires in approximately {remaining} seconds."
        )

    else:

        st.error("The OTP has expired.")

    st.markdown(
        f"""
        <div class="demo-box">
            <b>Demo OTP — In a real system this would be sent through SMS.</b>
            <br><br>
            <b>{st.session_state.demo_otp}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    otp_input = st.text_input(
        "Enter 6-digit OTP",
        max_chars=6,
        placeholder="Enter OTP"
    )

    if st.button(
        "Verify OTP",
        type="primary",
        use_container_width=True
    ):

        if otp_expired():

            st.error("The OTP has expired.")
            st.warning("Please request a new OTP.")

        elif st.session_state.otp_used:

            st.error("This OTP has already been used.")

        elif (
            len(otp_input) != 6
            or not otp_input.isdigit()
        ):

            st.error("Please enter a valid 6-digit OTP.")

        else:

            entered_hash = hash_otp(otp_input)

            if hmac.compare_digest(
                entered_hash,
                st.session_state.otp_hash
            ):

                st.session_state.otp_used = True
                st.session_state.otp_verified = True

                # Generate the pattern ONLY after OTP succeeds
                generate_dynamic_pattern()

                st.session_state.authentication_stage = "pattern"

                st.rerun()

            else:

                st.session_state.otp_attempts += 1

                remaining_attempts = (
                    3 -
                    st.session_state.otp_attempts
                )

                if remaining_attempts > 0:

                    st.error("Incorrect OTP.")

                    st.warning(
                        f"Remaining attempts: "
                        f"{remaining_attempts}"
                    )

                else:

                    st.error(
                        "Too many incorrect OTP attempts. "
                        "Please request a new OTP."
                    )

    st.divider()

    if st.button(
        "Resend OTP",
        use_container_width=True
    ):

        generate_new_otp()
        st.success("A new demo OTP has been generated.")
        st.rerun()

    if st.button(
        "← Back to Security PIN",
        use_container_width=True
    ):

        st.session_state.authentication_stage = "pin"
        st.session_state.otp_hash = ""
        st.session_state.demo_otp = ""
        st.session_state.otp_created_at = 0
        st.session_state.otp_attempts = 0
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# DYNAMIC PATTERN SCREEN
# ---------------------------------------------------------

elif st.session_state.authentication_stage == "pattern":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-title">Dynamic Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Remember the pattern shown below and reproduce it.'
        '</div>',
        unsafe_allow_html=True
    )

    pattern_text = " → ".join(
        str(x)
        for x in st.session_state.current_pattern
    )

    st.markdown(
        f"""
        <div class="pattern-display">
            Pattern: {pattern_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "This is a newly generated pattern for this authentication session."
    )

    st.subheader("Select the numbers in the same order")

    # 3x3 numbered grid
    for row in range(3):

        cols = st.columns(3)

        for col in range(3):

            number = row * 3 + col + 1

            with cols[col]:

                if st.button(
                    str(number),
                    key=f"pattern_{number}",
                    use_container_width=True
                ):

                    if number not in st.session_state.entered_pattern:

                        st.session_state.entered_pattern.append(
                            number
                        )

                    st.rerun()

    if st.session_state.entered_pattern:

        entered_text = " → ".join(
            str(x)
            for x in st.session_state.entered_pattern
        )

        st.write(
            f"**Pattern entered:** {entered_text}"
        )

    else:

        st.write(
            "**Pattern entered:** —"
        )

    if st.button(
        "Clear Pattern",
        use_container_width=True
    ):

        st.session_state.entered_pattern = []
        st.rerun()

    if st.button(
        "Verify Pattern",
        type="primary",
        use_container_width=True
    ):

        if not st.session_state.entered_pattern:

            st.error("Please select a pattern.")

        elif (
            st.session_state.entered_pattern
            == st.session_state.current_pattern
        ):

            st.session_state.pattern_verified = True
            st.session_state.login_status = True
            st.session_state.authentication_stage = "dashboard"

            st.success(
                "Pattern verified successfully."
            )

            st.rerun()

        else:

            st.session_state.pattern_attempts += 1

            remaining_attempts = (
                3 -
                st.session_state.pattern_attempts
            )

            if remaining_attempts > 0:

                st.error("Incorrect pattern.")

                st.warning(
                    f"Remaining attempts: "
                    f"{remaining_attempts}"
                )

                st.session_state.entered_pattern = []

            else:

                st.error(
                    "Pattern authentication failed. "
                    "Please restart login."
                )

                st.session_state.entered_pattern = []

                if st.button(
                    "Restart Login",
                    use_container_width=True
                ):

                    reset_authentication()
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# DEMO INFORMATION
# ---------------------------------------------------------

with st.expander("🔐 Academic Prototype / Demo Information"):

    st.write(
        """
        **Security PIN**

        The Security PIN is the first authentication factor.
        In this prototype, the demo PIN is 123456.
        """
    )

    st.write(
        """
        **OTP**

        A cryptographically secure 6-digit OTP is generated
        after successful Security PIN verification.
        The OTP expires after 60 seconds and has a maximum
        of three incorrect attempts.
        """
    )

    st.write(
        """
        **Dynamic Pattern**

        A new pattern containing 3–5 unique numbers from 1–9
        is generated only after successful OTP verification.
        """
    )

    st.write(
        """
        **Multi-Factor Authentication**

        Security PIN + OTP + Dynamic Pattern
        provides three sequential authentication factors
        in this academic prototype.
        """
    )

    st.write(
        """
        **Important**

        This is an academic demonstration.
        All documents and authentication information shown
        are dummy/sample data.
        """
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Secure DigiLocker | Academic Prototype<br>
        Independent educational project — not affiliated with DigiLocker.
    </div>
    """,
    unsafe_allow_html=True
)
