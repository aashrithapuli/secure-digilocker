import streamlit as st
import random
import hashlib
import time

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "stage": "login",
    "mobile": "",
    "pin": "",
    "enrolled_pattern": [],
    "selected_pattern": [],
    "physical_grid": list(range(1, 10)),
    "authenticated": False,
    "otp": "",
    "otp_hash": "",
    "otp_time": 0,
    "otp_attempts": 0,
    "otp_verified": False,
    "demo_otp_mode": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background: #f5f1ff;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .gov-header {
        background: #0b2167;
        color: white;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
    }

    .brand-box {
        background: white;
        padding: 22px 25px;
        border-bottom: 1px solid #ddd;
    }

    .brand-title {
        color: #4f32c8;
        font-size: 30px;
        font-weight: 700;
    }

    .brand-subtitle {
        color: #777;
        font-size: 14px;
        margin-top: 3px;
    }

    .prototype {
        display: inline-block;
        background: #eeeaff;
        color: #4f32c8;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 5px;
        margin-left: 8px;
    }

    .login-card {
        background: white;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(60, 40, 100, 0.12);
        margin-top: 25px;
        border: 1px solid #e3def2;
    }

    .title {
        font-size: 27px;
        font-weight: 700;
        color: #171717;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #777;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .info-box {
        background: #edf3ff;
        border-left: 4px solid #4267d5;
        padding: 13px;
        border-radius: 6px;
        margin: 15px 0;
        color: #18326f;
    }

    .pattern-title {
        font-size: 23px;
        font-weight: 700;
        color: #202020;
        margin-top: 10px;
    }

    .pattern-info {
        color: #666;
        margin-bottom: 15px;
    }

    .sequence {
        background: #f1edff;
        color: #4f32c8;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        margin: 12px 0;
    }

    .document-card {
        background: white;
        border: 1px solid #e3def2;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .document-title {
        font-size: 18px;
        font-weight: 700;
        color: #222;
    }

    .document-authority {
        color: #666;
        font-size: 13px;
        margin-top: 4px;
    }

    .document-status {
        color: #16803c;
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }

    .footer {
        text-align: center;
        color: #777;
        font-size: 12px;
        padding: 25px 0;
    }

    @media (max-width: 600px) {

        .main .block-container {
            padding: 0.5rem;
        }

        .login-card {
            padding: 20px;
            margin-top: 15px;
        }

        .title {
            font-size: 23px;
        }

        .brand-title {
            font-size: 25px;
        }

        .gov-header {
            font-size: 12px;
        }

        button {
            min-height: 48px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="gov-header">
        🇮🇳 Government of India &nbsp; | &nbsp; Secure Digital Services
    </div>

    <div class="brand-box">
        <div class="brand-title">
            🔐 Secure DigiLocker
            <span class="prototype">ACADEMIC PROTOTYPE</span>
        </div>

        <div class="brand-subtitle">
            Secure digital document access
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def hash_value(value):
    return hashlib.sha256(value.encode()).hexdigest()


def reset_pattern():
    st.session_state.selected_pattern = []


def generate_dynamic_grid():
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    st.session_state.physical_grid = numbers


def check_pattern():
    return (
        st.session_state.selected_pattern
        == st.session_state.enrolled_pattern
    )


def generate_otp():
    otp = str(random.randint(100000, 999999))

    st.session_state.otp = otp
    st.session_state.otp_hash = hash_value(otp)
    st.session_state.otp_time = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_verified = False


def otp_valid():
    return time.time() - st.session_state.otp_time <= 60


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if st.session_state.authenticated:

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="title">Welcome back!</div>
        <div class="subtitle">
            Your secure digital documents
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(
            "### 📁 My Documents"
        )

    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.stage = "login"
            st.session_state.selected_pattern = []
            st.rerun()

    documents = [
        ("🪪", "Aadhaar Card", "UIDAI", "Verified"),
        ("🚗", "Driving Licence", "Ministry of Road Transport", "Verified"),
        ("🗳️", "Voter ID", "Election Commission of India", "Verified"),
        ("🎓", "Class 10 Certificate", "Education Board", "Verified"),
        ("🎓", "Class 12 Certificate", "Education Board", "Verified"),
        ("🎓", "Degree Certificate", "University", "Verified"),
        ("📄", "PAN Card", "Income Tax Department", "Verified"),
        ("🏥", "Health Certificate", "Health Department", "Verified"),
        ("🏦", "Income Certificate", "Revenue Department", "Verified")
    ]

    for icon, name, authority, status in documents:

        st.markdown(
            f"""
            <div class="document-card">
                <div class="document-title">
                    {icon} {name}
                </div>

                <div class="document-authority">
                    Issuing Authority: {authority}
                </div>

                <div class="document-status">
                    ✓ {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            st.button(
                "View",
                key="view_" + name,
                use_container_width=True
            )

        with c2:
            st.button(
                "Download",
                key="download_" + name,
                use_container_width=True
            )

    st.markdown(
        """
        <div class="footer">
            Secure DigiLocker — Academic Prototype<br>
            Demo documents only. No real government documents are stored.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ---------------------------------------------------------
# PATTERN ENROLLMENT
# ---------------------------------------------------------

if st.session_state.stage == "enroll":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="pattern-title">Create Your Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Choose 3 or more numbers that you can remember."
    )

    st.info(
        "Example: You can choose 2 → 5 → 8 → 9. "
        "Your pattern will be used as an additional authentication layer."
    )

    cols = st.columns(3)

    for index in range(9):

        number = index + 1

        with cols[index % 3]:

            selected = number in st.session_state.selected_pattern

            label = (
                f"✓ {number}"
                if selected
                else str(number)
            )

            if st.button(
                label,
                key=f"enroll_{number}",
                use_container_width=True
            ):

                if number in st.session_state.selected_pattern:
                    st.session_state.selected_pattern.remove(number)
                else:
                    st.session_state.selected_pattern.append(number)

                st.rerun()

    if st.session_state.selected_pattern:

        sequence = " → ".join(
            map(str, st.session_state.selected_pattern)
        )

        st.markdown(
            f'<div class="sequence">Pattern selected: {sequence}</div>',
            unsafe_allow_html=True
        )

    else:

        st.caption("No pattern selected yet.")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Clear Pattern",
            use_container_width=True
        ):
            reset_pattern()
            st.rerun()

    with c2:

        if st.button(
            "Save Pattern",
            type="primary",
            use_container_width=True
        ):

            if len(st.session_state.selected_pattern) < 3:

                st.error(
                    "Please select at least 3 numbers."
                )

            else:

                st.session_state.enrolled_pattern = (
                    st.session_state.selected_pattern.copy()
                )

                st.session_state.selected_pattern = []

                st.success(
                    "Security pattern saved successfully."
                )

                st.session_state.stage = "login"

                time.sleep(1)

                st.rerun()

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ---------------------------------------------------------
# OTP DEMO
# ---------------------------------------------------------

if st.session_state.stage == "otp":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="title">OTP Verification</div>',
        unsafe_allow_html=True
    )

    st.write(
        "A simulated OTP has been generated for this academic prototype."
    )

    if not st.session_state.otp:
        generate_otp()

    remaining = max(
        0,
        60 - int(time.time() - st.session_state.otp_time)
    )

    st.info(
        f"Demo OTP — In a real system this would be sent through SMS."
    )

    st.code(
        st.session_state.otp
    )

    st.write(
        f"OTP expires in approximately {remaining} seconds."
    )

    if not otp_valid():

        st.error(
            "OTP expired. Please generate a new OTP."
        )

        if st.button(
            "Generate New OTP",
            use_container_width=True
        ):
            generate_otp()
            st.rerun()

    else:

        entered = st.text_input(
            "Enter OTP",
            max_chars=6,
            placeholder="6-digit OTP"
        )

        if st.button(
            "Verify OTP",
            type="primary",
            use_container_width=True
        ):

            if st.session_state.otp_attempts >= 3:

                st.error(
                    "Maximum attempts reached. Generate a new OTP."
                )

            elif hash_value(entered) == st.session_state.otp_hash:

                st.session_state.otp_verified = True
                st.session_state.otp = ""

                st.success(
                    "OTP verified successfully."
                )

                st.session_state.stage = "login"

                time.sleep(1)

                st.rerun()

            else:

                st.session_state.otp_attempts += 1

                st.error(
                    f"Incorrect OTP. "
                    f"Attempts remaining: "
                    f"{3 - st.session_state.otp_attempts}"
                )

    if st.button(
        "Back to Login",
        use_container_width=True
    ):
        st.session_state.stage = "login"
        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.stop()


# ---------------------------------------------------------
# DYNAMIC PATTERN LOGIN
# ---------------------------------------------------------

if st.session_state.stage == "pattern_login":

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="pattern-title">Security Pattern</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Select your previously created pattern."
    )

    st.info(
        "The number positions have been shuffled for this login."
    )

    cols = st.columns(3)

    for index, number in enumerate(
        st.session_state.physical_grid
    ):

        with cols[index % 3]:

            selected = (
                number
                in st.session_state.selected_pattern
            )

            label = (
                f"✓ {number}"
                if selected
                else str(number)
            )

            if st.button(
                label,
                key=f"login_pattern_{index}_{number}",
                use_container_width=True
            ):

                if number in st.session_state.selected_pattern:

                    st.session_state.selected_pattern.remove(
                        number
                    )

                else:

                    st.session_state.selected_pattern.append(
                        number
                    )

                st.rerun()

    if st.session_state.selected_pattern:

        sequence = " → ".join(
            map(str, st.session_state.selected_pattern)
        )

        st.markdown(
            f'<div class="sequence">Pattern entered: {sequence}</div>',
            unsafe_allow_html=True
        )

    else:

        st.caption("No pattern entered.")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Clear Pattern",
            use_container_width=True
        ):

            reset_pattern()
            st.rerun()

    with c2:

        if st.button(
            "Verify Pattern",
            type="primary",
            use_container_width=True
        ):

            if check_pattern():

                st.session_state.authenticated = True
                st.session_state.selected_pattern = []

                st.success(
                    "Authentication successful."
                )

                time.sleep(1)

                st.rerun()

            else:

                st.error(
                    "Authentication failed. Please try again."
                )

                st.session_state.selected_pattern = []

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.stop()


# ---------------------------------------------------------
# SECURITY PIN LOGIN
# ---------------------------------------------------------

st.markdown(
    '<div class="login-card">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="title">Login or Create Account</div>',
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
    <div class="info-box">
        Your mobile number is used only for this academic prototype.
        Do not enter real sensitive information.
    </div>
    """,
    unsafe_allow_html=True
)

pin = st.text_input(
    "Security PIN",
    type="password",
    max_chars=6,
    placeholder="Enter 6-digit Security PIN"
)

st.caption(
    "Demo: For the prototype, use any 6-digit PIN after creating your account."
)

if st.button(
    "Continue",
    type="primary",
    use_container_width=True
):

    if not mobile.isdigit() or len(mobile) != 10:

        st.error(
            "Please enter a valid 10-digit mobile number."
        )

    elif not pin.isdigit() or len(pin) != 6:

        st.error(
            "Please enter a valid 6-digit Security PIN."
        )

    else:

        st.session_state.mobile = mobile
        st.session_state.pin = hash_value(pin)

        if not st.session_state.enrolled_pattern:

            st.session_state.stage = "enroll"

            st.success(
                "Account details accepted. "
                "Now create your security pattern."
            )

        else:

            generate_dynamic_grid()

            st.session_state.selected_pattern = []

            st.session_state.stage = "pattern_login"

        time.sleep(0.5)

        st.rerun()


st.markdown(
    "---"
)

c1, c2 = st.columns(2)

with c1:

    if st.button(
        "Use OTP Demo",
        use_container_width=True
    ):

        st.session_state.stage = "otp"
        generate_otp()
        st.rerun()

with c2:

    st.button(
        "Need Help?",
        use_container_width=True
    )

st.markdown(
    """
    <div class="footer">
        By continuing, you agree to the Terms of Service.<br><br>
        Secure DigiLocker — Academic Prototype<br>
        This application uses dummy data and is not an official DigiLocker service.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)
