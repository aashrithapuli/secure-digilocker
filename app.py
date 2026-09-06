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

# -------------------- CSS --------------------

st.markdown("""
<style>
.stApp {
    background: #f5f1ff;
}

.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #172b4d;
    text-align: center;
}

.subtitle {
    font-size: 16px;
    color: #5f6b7a;
    text-align: center;
}

.gov-header {
    background: #10246b;
    color: white;
    padding: 14px 20px;
    font-weight: 600;
    margin-bottom: 25px;
    border-radius: 0;
}

.brand {
    font-size: 28px;
    font-weight: 700;
    color: #4d2bb3;
}

.prototype {
    background: #eee8ff;
    color: #5530b8;
    padding: 4px 9px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
}

.login-box {
    background: white;
    padding: 30px;
    border-radius: 18px;
    border: 1px solid #ddd6f3;
    box-shadow: 0 5px 20px rgba(60, 40, 120, 0.08);
}

.pattern-number {
    font-size: 26px;
    font-weight: 700;
}

.demo-box {
    background: #fff8df;
    border-left: 5px solid #e0a800;
    padding: 12px;
    border-radius: 8px;
}

.success-box {
    background: #e7f7ed;
    padding: 12px;
    border-radius: 8px;
}

.footer {
    text-align: center;
    color: #777;
    font-size: 13px;
    margin-top: 35px;
}

button {
    min-height: 45px !important;
}

@media (max-width: 600px) {
    .main-title {
        font-size: 26px;
    }

    .brand {
        font-size: 23px;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- Session State --------------------

defaults = {
    "stage": "mobile",
    "mobile_number": "",
    "security_pin_attempts": 0,
    "security_pin_verified": False,
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
    "font_size": 16
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- Helper Functions --------------------

PIN_HASH = hashlib.sha256("123456".encode()).hexdigest()


def hash_otp(otp):
    return hmac.new(
        b"academic-demo-secret",
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def generate_pattern():
    length = secrets.choice([3, 4, 5])
    return secrets.SystemRandom().sample(range(1, 10), length)


def reset_authentication():
    for key, value in defaults.items():
        st.session_state[key] = value


def generate_new_otp():
    otp = generate_otp()

    st.session_state.demo_otp = otp
    st.session_state.otp_hash = hash_otp(otp)
    st.session_state.otp_created_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.stage = "otp"


def generate_new_pattern():
    st.session_state.current_pattern = generate_pattern()
    st.session_state.entered_pattern = []
    st.session_state.pattern_attempts = 0
    st.session_state.stage = "pattern"


# -------------------- Header --------------------

st.markdown(
    '<div class="gov-header">🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(
        '<div class="brand">🔐 Secure DigiLocker</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<span class="prototype">ACADEMIC PROTOTYPE</span>',
        unsafe_allow_html=True
    )

st.caption("Secure digital document access")


# -------------------- Accessibility --------------------

with st.sidebar:
    st.header("Accessibility")

    st.session_state.font_size = st.slider(
        "Text size",
        min_value=14,
        max_value=24,
        value=st.session_state.font_size
    )

    st.markdown(
        f"<p style='font-size:{st.session_state.font_size}px;'>"
        "Accessibility preview text"
        "</p>",
        unsafe_allow_html=True
    )


# =========================================================
# MOBILE NUMBER
# =========================================================

if st.session_state.stage == "mobile":

    st.markdown("---")

    st.markdown(
        '<div class="main-title">Login or Create Account</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Enter your mobile number to proceed</div>',
        unsafe_allow_html=True
    )

    st.write("")

    mobile = st.text_input(
        "Mobile Number",
        placeholder="10-digit mobile number",
        max_chars=10
    )

    st.info(
        "This is an academic prototype. "
        "Do not enter real sensitive information."
    )

    if st.button(
        "Continue",
        use_container_width=True,
        type="primary"
    ):

        if not mobile.isdigit() or len(mobile) != 10:
            st.error("Please enter a valid 10-digit mobile number.")

        else:
            st.session_state.mobile_number = mobile
            st.session_state.security_pin_attempts = 0
            st.session_state.security_pin_verified = False
            st.session_state.stage = "pin"
            st.rerun()

    st.markdown("---")

    st.caption(
        "By continuing, I agree to the Terms of Service."
    )

    st.write("OR")

    if st.button(
        "📱 Login using QR Code",
        use_container_width=True
    ):
        st.info(
            "QR login is a demonstration feature in this prototype."
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
        '<div class="subtitle">'
        'Enter your 6-digit Security PIN to continue'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown(
        '<div class="demo-box">'
        '<b>Demo Security PIN: 123456</b>'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    pin = st.text_input(
        "Security PIN",
        type="password",
        max_chars=6,
        placeholder="Enter 6-digit PIN"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            st.session_state.stage = "mobile"
            st.rerun()

    with col2:
        if st.button(
            "Continue",
            use_container_width=True,
            type="primary"
        ):

            if len(pin) != 6 or not pin.isdigit():
                st.error("Security PIN must contain 6 digits.")

            else:
                entered_hash = hashlib.sha256(
                    pin.encode()
                ).hexdigest()

                if hmac.compare_digest(
                    entered_hash,
                    PIN_HASH
                ):

                    st.session_state.security_pin_verified = True

                    generate_new_otp()

                    st.success(
                        "Security PIN verified successfully."
                    )

                    st.rerun()

                else:

                    st.session_state.security_pin_attempts += 1

                    remaining = (
                        3 -
                        st.session_state.security_pin_attempts
                    )

                    if remaining > 0:

                        st.error(
                            f"Incorrect Security PIN. "
                            f"{remaining} attempt(s) remaining."
                        )

                    else:

                        st.error(
                            "Too many incorrect attempts. "
                            "Please restart authentication."
                        )

                        st.session_state.stage = "locked"


    if st.button(
        "Forgot Security PIN?",
        use_container_width=True
    ):
        st.info(
            "For this academic prototype, use the Demo Security PIN: 123456."
        )


# =========================================================
# LOCKED
# =========================================================

elif st.session_state.stage == "locked":

    st.error(
        "Authentication has been temporarily stopped "
        "because of too many incorrect attempts."
    )

    st.write(
        "Please restart authentication to try again."
    )

    if st.button(
        "Restart Login",
        use_container_width=True,
        type="primary"
    ):
        reset_authentication()
        st.rerun()


# =========================================================
# OTP
# =========================================================

elif st.session_state.stage == "otp":

    st.markdown(
        '<div class="main-title">OTP Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Enter the 6-digit OTP to continue'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    elapsed = time.time() - st.session_state.otp_created_at
    remaining_seconds = max(0, 60 - int(elapsed))

    if remaining_seconds == 0:

        st.error("The OTP has expired.")

        if st.button(
            "Resend OTP",
            use_container_width=True,
            type="primary"
        ):
            generate_new_otp()
            st.rerun()

    else:

        st.info(
            f"OTP expires in approximately "
            f"{remaining_seconds} seconds."
        )

        st.markdown(
            '<div class="demo-box">'
            '<b>Demo OTP — In a real system this would be sent through SMS.</b>'
            '</div>',
            unsafe_allow_html=True
        )

        st.code(
            st.session_state.demo_otp,
            language=None
        )

        otp_input = st.text_input(
            "Enter OTP",
            max_chars=6,
            placeholder="6-digit OTP"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Verify OTP",
                use_container_width=True,
                type="primary"
            ):

                elapsed = (
                    time.time() -
                    st.session_state.otp_created_at
                )

                if elapsed >= 60:

                    st.error("The OTP has expired.")

                elif st.session_state.otp_used:

                    st.error(
                        "This OTP has already been used."
                    )

                else:

                    entered_hash = hash_otp(
                        otp_input
                    )

                    if hmac.compare_digest(
                        entered_hash,
                        st.session_state.otp_hash
                    ):

                        st.session_state.otp_used = True
                        st.session_state.otp_verified = True

                        generate_new_pattern()

                        st.success(
                            "OTP verified successfully."
                        )

                        st.rerun()

                    else:

                        st.session_state.otp_attempts += 1

                        remaining = (
                            3 -
                            st.session_state.otp_attempts
                        )

                        if remaining > 0:

                            st.error(
                                f"Incorrect OTP. "
                                f"{remaining} attempt(s) remaining."
                            )

                        else:

                            st.error(
                                "Too many incorrect OTP attempts. "
                                "Please request a new OTP."
                            )

        with col2:

            if st.button(
                "Resend OTP",
                use_container_width=True
            ):
                generate_new_otp()
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
        '<div class="main-title">Dynamic Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Remember the pattern shown below and reproduce it.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    pattern_text = " → ".join(
        str(x)
        for x in st.session_state.current_pattern
    )

    st.info(
        f"Pattern: {pattern_text}"
    )

    st.write("Select the numbers in the same order.")

    # 3 x 3 numbered grid

    for row in range(3):

        cols = st.columns(3)

        for col in range(3):

            number = row * 3 + col + 1

            with cols[col]:

                if number in st.session_state.entered_pattern:

                    button_text = f"✓ {number}"

                else:

                    button_text = str(number)

                if st.button(
                    button_text,
                    key=f"pattern_{number}",
                    use_container_width=True
                ):

                    if number not in st.session_state.entered_pattern:

                        st.session_state.entered_pattern.append(
                            number
                        )

                    st.rerun()

    st.write("")

    entered_text = " → ".join(
        str(x)
        for x in st.session_state.entered_pattern
    )

    if entered_text:
        st.success(
            f"Pattern entered: {entered_text}"
        )
    else:
        st.write(
            "Pattern entered: —"
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Clear Pattern",
            use_container_width=True
        ):

            st.session_state.entered_pattern = []
            st.rerun()

    with col2:

        if st.button(
            "Verify Pattern",
            use_container_width=True,
            type="primary"
        ):

            if (
                st.session_state.entered_pattern
                ==
                st.session_state.current_pattern
            ):

                st.session_state.pattern_verified = True
                st.session_state.login_status = True
                st.session_state.stage = "dashboard"

                st.success(
                    "Pattern verified successfully."
                )

                st.rerun()

            else:

                st.session_state.pattern_attempts += 1

                remaining = (
                    3 -
                    st.session_state.pattern_attempts
                )

                st.session_state.entered_pattern = []

                if remaining > 0:

                    st.error(
                        f"Incorrect pattern. "
                        f"{remaining} attempt(s) remaining."
                    )

                else:

                    st.error(
                        "Pattern authentication failed. "
                        "Please restart login."
                    )

                    st.session_state.stage = "locked"


# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state.stage == "dashboard":

    st.markdown(
        '<div class="main-title">Secure DigiLocker</div>',
        unsafe_allow_html=True
    )

    st.success("Authentication completed successfully.")

    col1, col2 = st.columns([3, 1])

    with col1:

        st.header("Welcome back!")

        st.write(
            "Your secure digital documents are available below."
        )

    with col2:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            reset_authentication()
            st.rerun()

    st.divider()

    st.header("Important Documents")

    documents = [
        ("🪪", "Aadhaar Card", "UIDAI", "Verified", "15 Jan 2025"),
        ("🚗", "Driving Licence", "Transport Department", "Verified", "20 Feb 2025"),
        ("🗳️", "Voter ID", "Election Commission", "Verified", "10 Mar 2025"),
        ("🎓", "Class 10 Certificate", "Education Board", "Verified", "15 Apr 2025"),
        ("🎓", "Class 12 Certificate", "Education Board", "Verified", "20 May 2025"),
        ("🎓", "Degree Certificate", "University", "Verified", "10 Jun 2025"),
        ("📄", "PAN Card", "Income Tax Department", "Verified", "05 Jul 2025"),
        ("🏥", "Health Certificate", "Health Department", "Verified", "12 Aug 2025"),
        ("🏦", "Income Certificate", "Revenue Department", "Verified", "25 Aug 2025"),
        ("📑", "Other Documents", "Government Services", "Available", "01 Sep 2025")
    ]

    for i in range(0, len(documents), 2):

        col1, col2 = st.columns(2)

        doc1 = documents[i]

        with col1:

            with st.container(border=True):

                st.subheader(
                    f"{doc1[0]} {doc1[1]}"
                )

                st.write(
                    f"**Issuing Authority:** {doc1[2]}"
                )

                st.write(
                    f"**Status:** {doc1[3]}"
                )

                st.write(
                    f"**Issue Date:** {doc1[4]}"
                )

                b1, b2 = st.columns(2)

                with b1:

                    if st.button(
                        "View",
                        key=f"view_{i}",
                        use_container_width=True
                    ):
                        st.info(
                            f"Demo preview of {doc1[1]}."
                        )

                with b2:

                    if st.button(
                        "Download",
                        key=f"download_{i}",
                        use_container_width=True
                    ):
                        st.info(
                            "This academic prototype uses "
                            "dummy documents only."
                        )

        if i + 1 < len(documents):

            doc2 = documents[i + 1]

            with col2:

                with st.container(border=True):

                    st.subheader(
                        f"{doc2[0]} {doc2[1]}"
                    )

                    st.write(
                        f"**Issuing Authority:** {doc2[2]}"
                    )

                    st.write(
                        f"**Status:** {doc2[3]}"
                    )

                    st.write(
                        f"**Issue Date:** {doc2[4]}"
                    )

                    b1, b2 = st.columns(2)

                    with b1:

                        if st.button(
                            "View",
                            key=f"view_{i+1}",
                            use_container_width=True
                        ):
                            st.info(
                                f"Demo preview of {doc2[1]}."
                            )

                    with b2:

                        if st.button(
                            "Download",
                            key=f"download_{i+1}",
                            use_container_width=True
                        ):
                            st.info(
                                "This academic prototype uses "
                                "dummy documents only."
                            )

    st.divider()

    st.header("Authentication Security")

    with st.expander(
        "Academic Prototype / Demo"
    ):

        st.write(
            "Security PIN: First authentication factor."
        )

        st.write(
            "OTP: Verifies possession of the registered "
            "mobile number/device."
        )

        st.write(
            "OTP expiry: Each OTP is valid for 60 seconds."
        )

        st.write(
            "Attempt limitation: Maximum 3 incorrect "
            "attempts for PIN, OTP and pattern."
        )

        st.write(
            "One-time OTP: The OTP is invalidated after "
            "successful verification."
        )

        st.write(
            "Dynamic Pattern: A new 3–5 number pattern "
            "is generated after successful OTP verification."
        )

        st.write(
            "Combined authentication: Security PIN + OTP "
            "+ Dynamic Pattern."
        )

    st.markdown(
        '<div class="footer">'
        'Secure DigiLocker • Academic Prototype • '
        'Dummy documents only'
        '</div>',
        unsafe_allow_html=True
    )
