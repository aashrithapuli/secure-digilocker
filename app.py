import streamlit as st
import secrets
import hashlib
import hmac
import time
import random
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Secure DigiLocker",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONSTANTS
# ============================================================

OTP_EXPIRY = 60
MAX_OTP_ATTEMPTS = 3
MAX_LOGIN_FAILURES = 5

# Academic demo secret.
# In a real production system this must be stored securely.
HMAC_SECRET = b"academic-demo-secret-change-me"

ENROLLED_PATTERN = [1, 5, 9]

DOCUMENTS = [
    {
        "icon": "🪪",
        "name": "Aadhaar Card",
        "authority": "UIDAI",
        "status": "Issued",
        "date": "15 Jan 2025"
    },
    {
        "icon": "🚗",
        "name": "Driving Licence",
        "authority": "Transport Department",
        "status": "Issued",
        "date": "20 Mar 2025"
    },
    {
        "icon": "🗳️",
        "name": "Voter ID",
        "authority": "Election Commission",
        "status": "Issued",
        "date": "10 Apr 2025"
    },
    {
        "icon": "🎓",
        "name": "Class 10 Certificate",
        "authority": "Education Board",
        "status": "Issued",
        "date": "12 Jun 2022"
    },
    {
        "icon": "🎓",
        "name": "Class 12 Certificate",
        "authority": "Education Board",
        "status": "Issued",
        "date": "15 Jun 2024"
    },
    {
        "icon": "🎓",
        "name": "Degree Certificate",
        "authority": "University",
        "status": "Issued",
        "date": "25 Jun 2026"
    },
    {
        "icon": "📄",
        "name": "PAN Card",
        "authority": "Income Tax Department",
        "status": "Issued",
        "date": "05 Feb 2025"
    },
    {
        "icon": "🏥",
        "name": "Health Certificate",
        "authority": "Health Department",
        "status": "Issued",
        "date": "18 Aug 2025"
    },
    {
        "icon": "🏦",
        "name": "Income Certificate",
        "authority": "Revenue Department",
        "status": "Issued",
        "date": "02 Sep 2025"
    },
    {
        "icon": "📑",
        "name": "Other Documents",
        "authority": "Various Authorities",
        "status": "Issued",
        "date": "01 Jan 2026"
    }
]

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "login",
    "mobile": "",
    "otp_hash": "",
    "otp_time": 0,
    "demo_otp": "",
    "otp_attempts": 0,
    "login_failures": 0,
    "account_locked": False,
    "otp_used": False,
    "pattern": [],
    "grid": [],
    "pattern_attempts": 0,
    "authenticated": False,
    "auth_start": 0,
    "otp_time_taken": 0,
    "pattern_time_taken": 0,
    "session_time_taken": 0,
    "last_auth_result": "",
    "mode": "Demo Mode",
    "font_scale": 1.0,
    "requests": [],
    "sim_results": [],
    "notifications": 2
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# CSS
# ============================================================

scale = st.session_state.font_scale

st.markdown(
    f"""
    <style>

    html, body, [class*="css"] {{
        font-size: {scale}em;
    }}

    .stApp {{
        background-color: #f5f2ff;
    }}

    .topbar {{
        background-color: #17266b;
        color: white;
        padding: 14px 25px;
        margin: -70px -70px 25px -70px;
        font-size: 15px;
        font-weight: 600;
    }}

    .brand {{
        color: #5b2bbf;
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 20px;
    }}

    .card {{
        background-color: white;
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #ddd6ee;
        box-shadow: 0 5px 20px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }}

    .document-card {{
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #ddd6ee;
        margin-bottom: 12px;
    }}

    .demo {{
        background-color: #fff5d6;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #e5c76b;
        margin-bottom: 15px;
    }}

    .security {{
        background-color: #eaf7ee;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #9bd2aa;
        margin-bottom: 15px;
    }}

    .pattern-node {{
        font-size: 24px;
        font-weight: bold;
    }}

    @media (max-width: 768px) {{

        .topbar {{
            margin: -20px -20px 20px -20px;
            padding: 12px;
            font-size: 13px;
        }}

        .brand {{
            font-size: 24px;
        }}

        .card {{
            padding: 18px;
        }}

        button {{
            min-height: 48px !important;
        }}

        input {{
            min-height: 45px !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def hash_otp(otp):
    return hmac.new(
        HMAC_SECRET,
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def generate_grid():
    numbers = list(range(1, 10))
    secrets.SystemRandom().shuffle(numbers)
    return numbers


def reset_otp():
    otp = generate_otp()

    st.session_state.otp_hash = hash_otp(otp)
    st.session_state.demo_otp = otp
    st.session_state.otp_time = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False


def log_request(result, duration):
    st.session_state.requests.append(
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "result": result,
            "duration": round(duration, 3)
        }
    )

    if len(st.session_state.requests) > 100:
        st.session_state.requests.pop(0)


def clear_authentication():
    st.session_state.otp_hash = ""
    st.session_state.otp_time = 0
    st.session_state.demo_otp = ""
    st.session_state.otp_attempts = 0
    st.session_state.otp_used = False
    st.session_state.pattern = []
    st.session_state.grid = []
    st.session_state.pattern_attempts = 0
    st.session_state.authenticated = False


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="topbar">🇮🇳 Government Service Style • Academic Prototype</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand">☁️ Secure DigiLocker</div>',
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.subheader("Accessibility")

    if st.button("A+ Increase Text", use_container_width=True):
        st.session_state.font_scale = min(
            1.4,
            st.session_state.font_scale + 0.1
        )
        st.rerun()

    if st.button("A- Decrease Text", use_container_width=True):
        st.session_state.font_scale = max(
            0.8,
            st.session_state.font_scale - 0.1
        )
        st.rerun()

    st.divider()

    st.subheader("Authentication Mode")

    st.session_state.mode = st.radio(
        "Select mode",
        ["Demo Mode", "Security Mode"]
    )

    st.caption(
        "Demo Mode shows detailed information. "
        "Security Mode uses generic authentication errors."
    )

    st.divider()

    st.caption(
        "Secure DigiLocker is an independent academic prototype."
    )

# ============================================================
# LOGIN
# ============================================================

if st.session_state.page == "login":

    st.markdown(
        """
        <div class="card">
        <h1>Login or Create Account</h1>
        <p>Enter your mobile number to proceed.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.account_locked:

        st.error(
            "Account is temporarily locked because of repeated failed authentication attempts."
        )

        if st.button(
            "Start New Demo Session",
            use_container_width=True
        ):
            clear_authentication()
            st.session_state.account_locked = False
            st.session_state.login_failures = 0
            st.rerun()

        st.stop()

    col1, col2 = st.columns([1, 4])

    with col1:
        st.text_input(
            "Country",
            value="+91",
            disabled=True
        )

    with col2:
        mobile = st.text_input(
            "Mobile Number",
            placeholder="Enter 10-digit mobile number",
            max_chars=10
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

        else:

            start = time.perf_counter()

            st.session_state.mobile = mobile
            reset_otp()
            st.session_state.auth_start = time.perf_counter()
            st.session_state.page = "otp"

            duration = time.perf_counter() - start

            log_request("OTP Generated", duration)

            st.rerun()

    st.divider()

    if st.button(
        "▣  Login using QR Code",
        use_container_width=True
    ):
        st.info(
            "QR login is included as a UI demonstration."
        )

    st.caption(
        "By continuing, you agree to the Terms of Service and Privacy Policy."
    )

    st.caption(
        "Academic Prototype • No real identity documents or credentials are collected."
    )

# ============================================================
# OTP PAGE
# ============================================================

elif st.session_state.page == "otp":

    st.markdown(
        """
        <div class="card">
        <h1>Verify Mobile Number</h1>
        <p>Enter the OTP to continue.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    elapsed = int(time.time() - st.session_state.otp_time)
    remaining = OTP_EXPIRY - elapsed

    if st.session_state.otp_used:

        st.error("This OTP has already been used.")

        if st.button(
            "Generate New OTP",
            use_container_width=True
        ):
            reset_otp()
            st.rerun()

        st.stop()

    if remaining <= 0:

        st.error("OTP has expired.")

        if st.button(
            "Generate New OTP",
            type="primary",
            use_container_width=True
        ):
            reset_otp()
            st.rerun()

        st.stop()

    st.markdown(
        """
        <div class="demo">
        <b>Demo OTP</b><br>
        In a real system this would be sent through SMS.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.code(st.session_state.demo_otp)

    st.warning(
        f"OTP expires in {remaining} seconds."
    )

    st.progress(remaining / OTP_EXPIRY)

    st.write(
        f"Attempts used: {st.session_state.otp_attempts}/{MAX_OTP_ATTEMPTS}"
    )

    entered_otp = st.text_input(
        "Enter 6-digit OTP",
        max_chars=6,
        placeholder="Enter OTP"
    )

    if st.button(
        "Verify OTP",
        type="primary",
        use_container_width=True
    ):

        start = time.perf_counter()

        if st.session_state.otp_attempts >= MAX_OTP_ATTEMPTS:

            st.error(
                "Maximum OTP attempts reached. Generate a new OTP."
            )

        else:

            st.session_state.otp_attempts += 1

            entered_hash = hash_otp(entered_otp)

            correct = hmac.compare_digest(
                entered_hash,
                st.session_state.otp_hash
            )

            if correct and remaining > 0:

                st.session_state.otp_used = True

                st.session_state.otp_time_taken = (
                    time.perf_counter() - start
                )

                st.session_state.grid = generate_grid()
                st.session_state.pattern = []
                st.session_state.pattern_attempts = 0
                st.session_state.page = "pattern"

                log_request(
                    "OTP Success",
                    st.session_state.otp_time_taken
                )

                st.rerun()

            else:

                st.session_state.login_failures += 1

                duration = time.perf_counter() - start

                log_request(
                    "OTP Failure",
                    duration
                )

                if st.session_state.mode == "Demo Mode":

                    remaining_attempts = (
                        MAX_OTP_ATTEMPTS
                        - st.session_state.otp_attempts
                    )

                    st.error(
                        f"Incorrect OTP. "
                        f"Attempts remaining: {max(0, remaining_attempts)}"
                    )

                else:

                    st.error(
                        "Authentication failed."
                    )

                if st.session_state.login_failures >= MAX_LOGIN_FAILURES:

                    st.session_state.account_locked = True
                    st.error(
                        "Account has been locked because of repeated failures."
                    )

    if st.button(
        "Generate New OTP",
        use_container_width=True
    ):
        reset_otp()
        st.rerun()

    if st.button(
        "Back to Login",
        use_container_width=True
    ):
        st.session_state.page = "login"
        st.rerun()

# ============================================================
# PATTERN PAGE
# ============================================================

elif st.session_state.page == "pattern":

    st.markdown(
        """
        <div class="card">
        <h1>Dynamic Visual Pattern Authentication</h1>
        <p>Verify your remembered security pattern.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Your enrolled logical pattern is 1 → 5 → 9."
    )

    st.write(
        "The physical position of each logical node changes "
        "during every authentication."
    )

    grid = st.session_state.grid

    st.subheader("Current Physical Grid")

    for row in range(3):

        cols = st.columns(3)

        for col in range(3):

            index = row * 3 + col
            number = grid[index]

            with cols[col]:

                if st.button(
                    str(number),
                    key=f"pattern_{index}",
                    use_container_width=True
                ):

                    if number not in st.session_state.pattern:

                        st.session_state.pattern.append(number)

                    st.rerun()

    st.write("")

    if st.session_state.pattern:

        pattern_display = " → ".join(
            map(str, st.session_state.pattern)
        )

        st.success(
            f"Pattern entered: {pattern_display}"
        )

    else:

        st.info(
            "Pattern entered: None"
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Clear Pattern",
            use_container_width=True
        ):

            st.session_state.pattern = []
            st.rerun()

    with col2:

        if st.button(
            "Verify Pattern",
            type="primary",
            use_container_width=True
        ):

            start = time.perf_counter()

            st.session_state.pattern_attempts += 1

            correct_pattern = (
                st.session_state.pattern
                == ENROLLED_PATTERN
            )

            duration = time.perf_counter() - start

            st.session_state.pattern_time_taken = duration

            if correct_pattern:

                st.session_state.authenticated = True

                st.session_state.session_time_taken = (
                    time.perf_counter()
                    - st.session_state.auth_start
                )

                st.session_state.last_auth_result = "Success"

                log_request(
                    "Authentication Success",
                    st.session_state.session_time_taken
                )

                st.session_state.page = "dashboard"

                st.rerun()

            else:

                st.session_state.login_failures += 1

                log_request(
                    "Pattern Failure",
                    duration
                )

                if st.session_state.mode == "Demo Mode":

                    st.error(
                        "Incorrect pattern. "
                        "The required logical sequence is 1 → 5 → 9."
                    )

                else:

                    st.error(
                        "Authentication failed."
                    )

                st.session_state.pattern = []

                if st.session_state.login_failures >= MAX_LOGIN_FAILURES:

                    st.session_state.account_locked = True

                    st.error(
                        "Account locked because of repeated failures."
                    )

    st.caption(
        "The prototype demonstrates logical-node mapping. "
        "A production implementation should use a secure touch-drag component."
    )

# ============================================================
# DASHBOARD
# ============================================================

elif st.session_state.page == "dashboard":

    st.sidebar.success("Authenticated")

    navigation = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "My Documents",
            "Issued Documents",
            "Shared Documents",
            "Profile",
            "Help",
            "Performance Simulation",
            "Logout"
        ]
    )

    if navigation == "Logout":

        clear_authentication()
        st.session_state.page = "login"
        st.rerun()

    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    elif navigation == "Home":

        st.markdown(
            """
            <div class="card">
            <h1>Welcome back! 👋</h1>
            <p>Your secure digital document locker.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Documents", len(DOCUMENTS))

        with col2:
            st.metric("Verified", len(DOCUMENTS))

        with col3:
            st.metric(
                "Notifications",
                st.session_state.notifications
            )

        st.divider()

        st.subheader("Important Documents")

        important = DOCUMENTS[:6]

        for document in important:

            st.markdown(
                f"""
                <div class="document-card">

                <h3>{document["icon"]} {document["name"]}</h3>

                <p>
                <b>Issuing Authority:</b>
                {document["authority"]}
                </p>

                <p>
                <b>Status:</b>
                {document["status"]}
                </p>

                <p>
                <b>Issue Date:</b>
                {document["date"]}
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    elif navigation in [
        "My Documents",
        "Issued Documents"
    ]:

        st.header(navigation)

        for document in DOCUMENTS:

            st.markdown(
                f"""
                <div class="document-card">

                <h3>{document["icon"]} {document["name"]}</h3>

                <p>
                <b>Issuing Authority:</b>
                {document["authority"]}
                </p>

                <p>
                <b>Status:</b>
                {document["status"]}
                </p>

                <p>
                <b>Issue Date:</b>
                {document["date"]}
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            with col1:

                st.button(
                    "View",
                    key=f"view_{document['name']}",
                    use_container_width=True
                )

            with col2:

                st.download_button(
                    "Download Demo",
                    data=(
                        "SECURE DIGILOCKER ACADEMIC PROTOTYPE\n\n"
                        f"Document: {document['name']}\n"
                        f"Issuing Authority: {document['authority']}\n"
                        f"Status: {document['status']}\n"
                        f"Issue Date: {document['date']}\n\n"
                        "This is dummy data and not an official document."
                    ),
                    file_name=(
                        document["name"]
                        .replace(" ", "_")
                        + ".txt"
                    ),
                    key=f"download_{document['name']}",
                    use_container_width=True
                )

    # --------------------------------------------------------
    # SHARED DOCUMENTS
    # --------------------------------------------------------

    elif navigation == "Shared Documents":

        st.header("Shared Documents")

        st.info(
            "This prototype contains sample sharing information only."
        )

        for document in DOCUMENTS[:4]:

            st.markdown(
                f"""
                <div class="document-card">

                <h3>{document["icon"]} {document["name"]}</h3>

                <p>Shared with: Academic Demo User</p>

                <p>Status: Active</p>

                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    elif navigation == "Profile":

        st.header("Profile")

        st.info(
            "Personal information is intentionally not collected."
        )

        st.write(
            f"**Demo Mobile:** +91 XXXXX{st.session_state.mobile[-4:]}"
        )

        st.write(
            "**Authentication:** OTP + Dynamic Pattern"
        )

        st.write(
            "**Account Status:** Active"
        )

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    elif navigation == "Help":

        st.header("Help")

        with st.expander("How does OTP authentication work?"):

            st.write(
                "A random 6-digit OTP is generated, hashed for "
                "verification, expires after 60 seconds, and "
                "becomes invalid after successful use."
            )

        with st.expander("How does dynamic pattern authentication work?"):

            st.write(
                "The logical pattern remains 1 → 5 → 9 while "
                "the physical positions of nodes are shuffled "
                "for every authentication session."
            )

        with st.expander("What happens after repeated failures?"):

            st.write(
                "The prototype limits OTP attempts and can "
                "temporarily lock the account after repeated "
                "authentication failures."
            )

    # ========================================================
    # PERFORMANCE SIMULATION
    # ========================================================

    elif navigation == "Performance Simulation":

        st.header("Authentication Performance Simulation")

        st.caption(
            "These values simulate system behavior for an academic project."
        )

        st.subheader("Current Authentication Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "OTP Time",
                f"{st.session_state.otp_time_taken:.4f}s"
            )

        with col2:
            st.metric(
                "Pattern Time",
                f"{st.session_state.pattern_time_taken:.4f}s"
            )

        with col3:
            st.metric(
                "Session Time",
                f"{st.session_state.session_time_taken:.4f}s"
            )

        with col4:

            successful = sum(
                1
                for r in st.session_state.requests
                if r["result"] == "Authentication Success"
            )

            total = len(st.session_state.requests)

            success_rate = (
                (successful / total) * 100
                if total > 0
                else 0
            )

            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%"
            )

        st.divider()

        # ----------------------------------------------------
        # REQUEST SIMULATION
        # ----------------------------------------------------

        st.subheader("Concurrent Request Simulation")

        request_count = st.slider(
            "Number of simulated login requests",
            min_value=1,
            max_value=100,
            value=20
        )

        server_capacity = st.slider(
            "Server requests processed at once",
            min_value=1,
            max_value=20,
            value=5
        )

        if st.button(
            "Run Request Simulation",
            type="primary",
            use_container_width=True
        ):

            results = []

            queue_length = 0

            for i in range(request_count):

                processing_time = random.uniform(
                    0.08,
                    0.35
                )

                if i >= server_capacity:

                    queue_length += 1

                    processing_time += random.uniform(
                        0.05,
                        0.20
                    )

                results.append(
                    {
                        "Request": i + 1,
                        "Processing Time": round(
                            processing_time,
                            3
                        ),
                        "Queued": (
                            "Yes"
                            if i >= server_capacity
                            else "No"
                        )
                    }
                )

            st.session_state.sim_results = results

            st.success(
                "Concurrent request simulation completed."
            )

        if st.session_state.sim_results:

            average_time = sum(
                r["Processing Time"]
                for r in st.session_state.sim_results
            ) / len(st.session_state.sim_results)

            queued = sum(
                1
                for r in st.session_state.sim_results
                if r["Queued"] == "Yes"
            )

            st.metric(
                "Average Response Time",
                f"{average_time:.3f}s"
            )

            st.metric(
                "Queued Requests",
                queued
            )

            st.dataframe(
                st.session_state.sim_results,
                use_container_width=True
            )

        st.divider()

        # ----------------------------------------------------
        # RESOURCE UTILIZATION
        # ----------------------------------------------------

        st.subheader("Simulated Resource Utilization")

        load = min(
            100,
            int(
                20
                + request_count * 0.7
                + random.uniform(0, 15)
            )
        )

        cpu = min(
            100,
            int(
                15
                + request_count * 0.6
            )
        )

        memory = min(
            100,
            int(
                30
                + request_count * 0.3
            )
        )

        database = min(
            100,
            int(
                20
                + request_count * 0.5
            )
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Server Load",
                f"{load}%"
            )

        with col2:
            st.metric(
                "CPU",
                f"{cpu}%"
            )

        with col3:
            st.metric(
                "Memory",
                f"{memory}%"
            )

        with col4:
            st.metric(
                "Database",
                f"{database}%"
            )

        st.progress(load / 100)

        if load >= 80:

            st.warning(
                "High server load detected."
            )

        elif load >= 60:

            st.info(
                "Moderate server load detected."
            )

        else:

            st.success(
                "Server load is within the simulated normal range."
            )

        st.divider()

        # ----------------------------------------------------
        # BOTTLENECK ANALYSIS
        # ----------------------------------------------------

        st.subheader("Authentication Bottleneck Analysis")

        bottlenecks = [
            {
                "Stage": "Mobile Validation",
                "Problem": "Invalid input or repeated requests",
                "Improvement": "Early input validation"
            },
            {
                "Stage": "OTP Generation",
                "Problem": "High request volume",
                "Improvement": "Efficient request handling"
            },
            {
                "Stage": "OTP Verification",
                "Problem": "Repeated failed attempts",
                "Improvement": "Attempt limits and lockout"
            },
            {
                "Stage": "Database Lookup",
                "Problem": "High concurrent access",
                "Improvement": "Caching and optimized queries"
            },
            {
                "Stage": "Pattern Verification",
                "Problem": "Additional authentication step",
                "Improvement": "Efficient verification logic"
            },
            {
                "Stage": "Session Creation",
                "Problem": "Server-side processing delay",
                "Improvement": "Resource allocation"
            }
        ]

        st.dataframe(
            bottlenecks,
            use_container_width=True
        )

        st.divider()

        # ----------------------------------------------------
        # IMPROVEMENT MATRIX
        # ----------------------------------------------------

        st.subheader("Performance Improvement Matrix")

        improvements = [
            {
                "Challenge": "Login Delay",
                "Proposed Improvement": "Queue Optimization",
                "Expected Benefit": "Faster Authentication"
            },
            {
                "Challenge": "Server Overload",
                "Proposed Improvement": "Better Resource Allocation",
                "Expected Benefit": "Reduced Waiting Time"
            },
            {
                "Challenge": "Unauthorized Access",
                "Proposed Improvement": "OTP + Pattern MFA",
                "Expected Benefit": "Enhanced Security"
            },
            {
                "Challenge": "Repeated OTP Attempts",
                "Proposed Improvement": "Attempt Limitation",
                "Expected Benefit": "Reduced Abuse"
            },
            {
                "Challenge": "OTP Replay",
                "Proposed Improvement": "One-Time OTP Usage",
                "Expected Benefit": "Replay Prevention"
            },
            {
                "Challenge": "Expired OTP",
                "Proposed Improvement": "Time-Limited OTP",
                "Expected Benefit": "Reduced Attack Window"
            },
            {
                "Challenge": "High Concurrent Requests",
                "Proposed Improvement": "Load Management",
                "Expected Benefit": "Improved Scalability"
            }
        ]

        st.dataframe(
            improvements,
            use_container_width=True
        )

        st.divider()

        # ----------------------------------------------------
        # REQUEST HISTORY
        # ----------------------------------------------------

        st.subheader("Authentication Request History")

        if st.session_state.requests:

            st.dataframe(
                st.session_state.requests,
                use_container_width=True
            )

        else:

            st.info(
                "No authentication requests recorded yet."
            )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Secure DigiLocker • Academic Prototype • "
    "OTP + Dynamic Visual Pattern Authentication"
)