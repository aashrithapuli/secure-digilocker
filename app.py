import streamlit as st
import secrets
import hashlib
import hmac
import time

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="centered"
)

OTP_EXPIRY = 60
MAX_OTP_ATTEMPTS = 3

# Demo secret - no secrets.toml is required
HMAC_SECRET = b"secure-digilocker-academic-demo"

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "page": "login",
    "mobile": "",
    "otp_hash": "",
    "demo_otp": "",
    "otp_time": 0.0,
    "otp_attempts": 0,
    "otp_used": False,
    "challenge": [],
    "challenge_used": False,
    "pattern_input": [],
    "authenticated": False,
    "font_scale": 1.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

fs = st.session_state.font_scale

st.markdown(
    f"""
    <style>

    .stApp {{
        background: #f5f1ff;
        font-size: {fs}rem;
    }}

    .govbar {{
        background: #17276b;
        color: white;
        padding: 11px 16px;
        font-weight: 700;
        font-size: 13px;
    }}

    .brand {{
        background: white;
        padding: 17px 16px;
        border-bottom: 1px solid #dddddd;
    }}

    .brand-name {{
        font-size: 25px;
        font-weight: 800;
        color: #5636d2;
    }}

    .sub {{
        font-size: 13px;
        color: #666666;
    }}

    .badge {{
        background: #fff1c7;
        color: #735300;
        border-radius: 10px;
        padding: 3px 7px;
        font-size: 10px;
    }}

    .card {{
        background: white;
        border: 1px solid #dddddd;
        border-radius: 18px;
        padding: 24px;
        margin: 22px 0;
        box-shadow: 0 5px 20px rgba(50, 30, 100, 0.07);
    }}

    .title {{
        font-size: 27px;
        font-weight: 800;
        color: #171a2a;
    }}

    .subtitle {{
        color: #666d7c;
        line-height: 1.5;
    }}

    .info {{
        background: #edf4ff;
        border-left: 4px solid #3d73d1;
        padding: 13px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    .demo {{
        background: #fff8df;
        border: 1px solid #e5d18b;
        border-radius: 10px;
        padding: 14px;
        margin: 15px 0;
    }}

    .otp {{
        text-align: center;
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 6px;
        color: #4930bd;
        padding: 8px;
    }}

    .challenge {{
        background: #f5f2ff;
        border: 2px solid #ddd4ff;
        border-radius: 15px;
        padding: 18px;
        text-align: center;
        margin: 18px 0;
    }}

    .sequence {{
        background: #eeeaff;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: #4329ad;
        font-weight: 800;
        margin: 15px 0;
    }}

    .doc {{
        background: white;
        border: 1px solid #dddddd;
        border-radius: 14px;
        padding: 16px;
        margin: 10px 0;
    }}

    .docicon {{
        font-size: 28px;
    }}

    .doctitle {{
        font-size: 18px;
        font-weight: 800;
    }}

    .meta {{
        font-size: 13px;
        color: #666666;
        line-height: 1.6;
    }}

    .status {{
        background: #e7f7ee;
        color: #176b43;
        padding: 4px 8px;
        border-radius: 12px;
        font-weight: 700;
    }}

    div.stButton > button {{
        min-height: 48px;
        border-radius: 10px;
        font-weight: 700;
    }}

    .footer {{
        text-align: center;
        color: #73798a;
        font-size: 12px;
        padding: 25px 10px 35px;
    }}

    @media (max-width: 600px) {{

        .card {{
            padding: 18px;
            margin: 18px 0;
        }}

        .title {{
            font-size: 23px;
        }}

        .brand-name {{
            font-size: 21px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

def header():

    st.markdown(
        """
        <div class="govbar">
            🇮🇳 Government of India | Secure Digital Services
        </div>

        <div class="brand">

            <div class="brand-name">
                🔐 Secure DigiLocker
                <span class="badge">
                    ACADEMIC PROTOTYPE
                </span>
            </div>

            <div class="sub">
                Secure digital document access
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

def footer():

    st.markdown(
        """
        <div class="footer">

        Secure DigiLocker is an independent academic prototype.<br>

        It is not connected to or operated by the official DigiLocker service.

        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# OTP FUNCTIONS
# ---------------------------------------------------------

def otp_digest(otp):

    return hmac.new(
        HMAC_SECRET,
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_otp():

    otp = f"{secrets.randbelow(1000000):06d}"

    st.session_state.demo_otp = otp

    st.session_state.otp_hash = otp_digest(otp)

    st.session_state.otp_time = time.time()

    st.session_state.otp_attempts = 0

    st.session_state.otp_used = False


def otp_expired():

    return (
        time.time() -
        st.session_state.otp_time
        >= OTP_EXPIRY
    )


# ---------------------------------------------------------
# VISUAL CHALLENGE
# ---------------------------------------------------------

def generate_challenge():

    numbers = list(range(1, 10))

    secrets.SystemRandom().shuffle(numbers)

    length = secrets.choice([3, 4, 5])

    st.session_state.challenge = numbers[:length]

    st.session_state.challenge_used = False

    st.session_state.pattern_input = []


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

def logout():

    for key, value in defaults.items():

        st.session_state[key] = value

    st.rerun()


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    header()

    st.markdown(
        """
        <div class="card">

            <div class="title">
                Login or Create Account
            </div>

            <div class="subtitle">
                Enter your mobile number to proceed
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    mobile = st.text_input(
        "Mobile number",
        placeholder="Enter 10-digit mobile number",
        max_chars=10
    )

    st.caption(
        "Academic prototype: no real SMS is sent."
    )

    if st.button(
        "Continue",
        type="primary"
    ):

        if (
            len(mobile) != 10
            or not mobile.isdigit()
            or mobile[0] not in "6789"
        ):

            st.error(
                "Enter a valid 10-digit Indian mobile number."
            )

        else:

            st.session_state.mobile = mobile

            generate_otp()

            st.session_state.page = "otp"

            st.rerun()

    st.markdown("---")

    st.markdown(
        "<center><b>OR</b></center>",
        unsafe_allow_html=True
    )

    if st.button("▣ Login using QR Code"):

        st.info(
            "QR login is a demonstration placeholder."
        )

    st.markdown(
        "<center>♿ Accessibility</center>",
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:

        if st.button("A−"):

            st.session_state.font_scale = max(
                0.85,
                fs - 0.05
            )

            st.rerun()

    with b:

        if st.button("A"):

            st.session_state.font_scale = 1.0

            st.rerun()

    with c:

        if st.button("A+"):

            st.session_state.font_scale = min(
                1.25,
                fs + 0.05
            )

            st.rerun()

    footer()


# =========================================================
# OTP PAGE
# =========================================================

def otp_page():

    header()

    st.markdown(
        """
        <div class="card">

            <div class="title">
                Verify Mobile Number
            </div>

            <div class="subtitle">
                Enter the OTP generated for this
                academic demonstration.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    remaining = max(
        0,
        int(
            OTP_EXPIRY -
            (time.time() - st.session_state.otp_time)
        )
    )

    st.markdown(
        f"""
        <div class="demo">

            <b>
            Demo OTP — In a real system this
            would be sent through SMS.
            </b>

            <div class="otp">
                {st.session_state.demo_otp}
            </div>

            <center>
                Expires in approximately
                {remaining} seconds
            </center>

        </div>
        """,
        unsafe_allow_html=True
    )

    if otp_expired():

        st.error("OTP has expired.")

        if st.button(
            "Generate New OTP",
            type="primary"
        ):

            generate_otp()

            st.rerun()

        if st.button("Back to Login"):

            logout()

        footer()

        return

    if (
        st.session_state.otp_attempts
        >= MAX_OTP_ATTEMPTS
    ):

        st.error(
            "Maximum OTP attempts reached."
        )

        if st.button(
            "Generate New OTP",
            type="primary"
        ):

            generate_otp()

            st.rerun()

        footer()

        return

    entered = st.text_input(
        "Enter OTP",
        max_chars=6,
        placeholder="6-digit OTP"
    )

    if st.button(
        "Verify OTP",
        type="primary"
    ):

        if (
            len(entered) != 6
            or not entered.isdigit()
        ):

            st.error(
                "Enter exactly 6 digits."
            )

        elif otp_expired():

            st.error(
                "OTP has expired."
            )

        elif st.session_state.otp_used:

            st.error(
                "This OTP has already been used."
            )

        elif hmac.compare_digest(
            otp_digest(entered),
            st.session_state.otp_hash
        ):

            st.session_state.otp_used = True

            generate_challenge()

            st.session_state.page = "challenge"

            st.rerun()

        else:

            st.session_state.otp_attempts += 1

            left = (
                MAX_OTP_ATTEMPTS -
                st.session_state.otp_attempts
            )

            if left > 0:

                st.error(
                    f"Incorrect OTP. "
                    f"Attempts remaining: {left}"
                )

            else:

                st.error(
                    "Three incorrect attempts reached. "
                    "Generate a new OTP."
                )

    if st.button(
        "Resend / Generate New OTP"
    ):

        generate_otp()

        st.rerun()

    if st.button("Cancel"):

        logout()

    footer()


# =========================================================
# DYNAMIC VISUAL CHALLENGE PAGE
# =========================================================

def challenge_page():

    header()

    st.markdown(
        """
        <div class="card">

            <div class="title">
                Dynamic Visual Challenge
            </div>

            <div class="subtitle">

                A fresh visual challenge has been
                generated for this login.

                Reproduce it using the numbered
                3×3 grid.

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    challenge_text = " → ".join(
        map(
            str,
            st.session_state.challenge
        )
    )

    st.markdown(
        f"""
        <div class="challenge">

            <b>
                Copy this one-time pattern
            </b>

            <div style="
                font-size:30px;
                font-weight:900;
                color:#4930bd;
                margin-top:10px;
            ">

                {challenge_text}

            </div>

            <div style="
                color:#666;
                margin-top:7px;
            ">

                This challenge changes on
                the next authentication.

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### Reproduce the pattern"
    )

    cols = st.columns(3)

    for number in range(1, 10):

        with cols[(number - 1) % 3]:

            selected = (
                number
                in st.session_state.pattern_input
            )

            if selected:

                label = f"✓ {number}"

            else:

                label = str(number)

            if st.button(
                label,
                key=f"pattern_{number}",
                type=(
                    "primary"
                    if selected
                    else "secondary"
                )
            ):

                if number in st.session_state.pattern_input:

                    st.session_state.pattern_input.remove(
                        number
                    )

                else:

                    st.session_state.pattern_input.append(
                        number
                    )

                st.rerun()

    if st.session_state.pattern_input:

        entered = " → ".join(
            map(
                str,
                st.session_state.pattern_input
            )
        )

    else:

        entered = "No pattern entered"

    st.markdown(
        f"""
        <div class="sequence">

            Pattern entered:
            {entered}

        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:

        if st.button(
            "Clear Pattern"
        ):

            st.session_state.pattern_input = []

            st.rerun()

    with right:

        if st.button(
            "Verify Pattern",
            type="primary"
        ):

            if st.session_state.challenge_used:

                st.error(
                    "This challenge has already been used."
                )

            elif (
                st.session_state.pattern_input
                == st.session_state.challenge
            ):

                st.session_state.challenge_used = True

                st.session_state.authenticated = True

                st.session_state.page = "dashboard"

                st.rerun()

            else:

                st.error(
                    "Pattern does not match the current challenge."
                )

    st.markdown(
        """
        <div class="info">

        <b>Research concept:</b>

        A new visual challenge is generated
        for every login.

        A successfully used challenge
        cannot be reused.

        </div>
        """,
        unsafe_allow_html=True
    )

    footer()


# =========================================================
# DOCUMENT DASHBOARD
# =========================================================

def dashboard_page():

    header()

    st.markdown(
        """
        <div class="card">

            <div class="title">
                Welcome back!
            </div>

            <div class="subtitle">
                Your Documents
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.success(
        "Authentication successful: "
        "OTP + dynamic visual challenge verified."
    )

    navigation = st.selectbox(
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

    if navigation == "Profile":

        st.markdown(
            """
            <div class="card">

                <h3>Profile</h3>

                <p>
                    Mobile: +91 ••••••
                </p>

                <p>
                    OTP authentication: Enabled
                </p>

                <p>
                    Dynamic visual challenge: Enabled
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    elif navigation == "Help":

        st.markdown(
            """
            <div class="card">

                <div class="title">
                    Security Information
                </div>

                <div class="subtitle">

                    • Secure random OTP generation<br>
                    • HMAC/SHA-256 OTP verification<br>
                    • 60-second OTP expiry<br>
                    • Maximum 3 OTP attempts<br>
                    • One-time OTP usage<br>
                    • Replay prevention<br>
                    • New visual challenge for every login<br>
                    • Combined OTP + visual authentication

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    elif navigation == "Shared Documents":

        st.info(
            "No sample shared documents are available."
        )

    else:

        if navigation == "Home":

            st.info(
                "Sample documents only. "
                "No real government documents are stored."
            )

        documents = [
            (
                "🪪",
                "Aadhaar Card",
                "UIDAI",
                "15 Jan 2026"
            ),
            (
                "🚗",
                "Driving Licence",
                "Transport Department",
                "02 Feb 2026"
            ),
            (
                "🗳️",
                "Voter ID",
                "Election Commission",
                "20 Feb 2026"
            ),
            (
                "🎓",
                "Class 10 Certificate",
                "Education Board",
                "10 Mar 2026"
            ),
            (
                "🎓",
                "Class 12 Certificate",
                "Education Board",
                "12 Mar 2026"
            ),
            (
                "🎓",
                "Degree Certificate",
                "University",
                "18 Apr 2026"
            ),
            (
                "📄",
                "PAN Card",
                "Income Tax Department",
                "22 Apr 2026"
            ),
            (
                "🏦",
                "Income Certificate",
                "Revenue Department",
                "05 May 2026"
            )
        ]

        for icon, name, authority, date in documents:

            st.markdown(
                f"""
                <div class="doc">

                    <div class="docicon">
                        {icon}
                    </div>

                    <div class="doctitle">
                        {name}
                    </div>

                    <div class="meta">

                        Issuing authority:
                        {authority}<br>

                        Issue date:
                        {date}<br>

                        <span class="status">
                            Available
                        </span>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "View",
                    key="view_" + name
                ):

                    st.info(
                        f"Demo preview of {name}."
                    )

            with c2:

                if st.button(
                    "Download",
                    key="download_" + name
                ):

                    st.info(
                        "Demo only — no real document is downloaded."
                    )

    if st.button(
        "Logout",
        type="primary"
    ):

        logout()

    footer()


# =========================================================
# PAGE ROUTER
# =========================================================

if st.session_state.page == "login":

    login_page()

elif st.session_state.page == "otp":

    otp_page()

elif st.session_state.page == "challenge":

    challenge_page()

elif st.session_state.page == "dashboard":

    dashboard_page()

else:

    logout()
