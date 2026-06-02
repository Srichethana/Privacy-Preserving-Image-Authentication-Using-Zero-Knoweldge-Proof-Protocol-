import streamlit as st
import tempfile
import os
import pandas as pd
import json
import plotly.express as px
from user_authentication import register
from zkp_login import zkp_login
from authentication_server import analytics

st.set_page_config(page_title="Image Authentication System", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    h1 {color: #1f2937; font-weight: 700; font-size: 2.8rem;}
    h2 {color: #374151; font-weight: 600;}
    .stButton>button {background-color: #2563eb; color: white;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Privacy-Preserving Image Authentication System using ZKP")
st.sidebar.markdown("Hospital Patient Portal")

page = st.sidebar.selectbox(
    "Select Page",
    ["Home", "Register", "Login", "Registered Patients", "Analytics"]
)

# Safe session state initialization
if 'last_round_times' not in st.session_state:
    st.session_state.last_round_times = None
if 'last_rounds_count' not in st.session_state:
    st.session_state.last_rounds_count = 5

# ==================== HOME PAGE ====================
if page == "Home":
    st.title("Privacy-Preserving Image Authentication System using ZKP")
    st.subheader("Privacy-Preserving Authentication for Hospital Patient Portal")
    
    st.markdown("""
    This system allows patients to securely access their medical records using a personal image as the secret key. 
    
    The actual image is **never stored** on the hospital server. Only its cryptographic hash is saved.
    
    During login, **Zero-Knowledge Proof (ZKP)** is used to verify the patient's identity without revealing the secret image.
    """)
    
    st.info("""
    **Key Benefits:**
    - High privacy protection for sensitive medical data
    - No need for traditional passwords
    - Secure authentication using image as secret
    - Replay attack prevention using nonce and session management
    """)

    st.markdown("### How It Works")
    st.write("1. Patient registers with a secret image")
    st.write("2. System stores only the hash of the image")
    st.write("3. During login, ZKP challenge-response verifies the user")
    st.write("4. Multiple rounds ensure higher security")

# ==================== REGISTER ====================
elif page == "Register":
    st.title("Patient Registration")
    username = st.text_input("Patient ID")
    image_file = st.file_uploader("Select Secret Image", type=["jpg", "jpeg", "png"])
    
    if st.button("Register Patient"):
        if username and image_file:
            with st.spinner("Processing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as tmp:
                    tmp.write(image_file.getvalue())
                    temp_path = tmp.name
                success, msg = register(username, temp_path)
                os.unlink(temp_path)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

# ==================== LOGIN ====================
elif page == "Login":
    st.title("Patient Secure Login")
    username = st.text_input("Patient ID")
    image_file = st.file_uploader("Select your registered secret image", type=["jpg", "jpeg", "png"])
    rounds = st.selectbox("Number of ZKP Rounds", [3, 5, 7], index=1)
    
    if st.button("Start Secure Authentication"):
        if username and image_file:
            with st.spinner(f"Running {rounds} rounds of ZKP..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as tmp:
                    tmp.write(image_file.getvalue())
                    temp_path = tmp.name
                
                success, message, total_time, round_details, round_times = zkp_login(username, temp_path, rounds)
                os.unlink(temp_path)
            
            if success:
                st.success("✅ Authentication Successful")
                st.write(f"Total Time: {total_time} seconds")
                
                st.session_state.last_round_times = round_times
                st.session_state.last_rounds_count = rounds
            else:
                st.error("❌ " + message)
        else:
            st.warning("Please provide Patient ID and image file.")

# ==================== REGISTERED PATIENTS ====================
elif page == "Registered Patients":
    st.title("Registered Patients")
    st.markdown("List of all registered patients (only cryptographic hashes are stored)")
    
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        data = []
        for pid, info in users.items():
            hash_value = info.get("hash", info) if isinstance(info, dict) else info
            data.append({
                "Patient ID": pid,
                "Secret Hash (first 16 characters)": hash_value[:16] + "..."
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    except:
        st.warning("No patients registered yet.")

# ==================== ANALYTICS PAGE ====================
elif page == "Analytics":
    st.title("Authentication Analytics")
    st.markdown("System security and performance insights")

    # ==================== NEW TEXT REPORT (exactly as in your image) ====================
    st.subheader("Authentication Analytics Report")
    report = analytics.get_report()
    st.text(report)

    # Original content (kept exactly the same)
    total_fail = sum(analytics.user_failures.values())
    total_attempts = analytics.success_count + total_fail
    success_rate = round((analytics.success_count / total_attempts * 100), 1) if total_attempts > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Successful Logins", analytics.success_count)
    with col2:
        st.metric("Total Failures", total_fail)
    with col3:
        st.metric("Success Rate", f"{success_rate}%")

    st.subheader("Success vs Failed Attempts")
    fig1 = px.bar(
        x=["Successful", "Failed"],
        y=[analytics.success_count, total_fail],
        color=["#00cc66", "#ff4d4d"],
        title="Authentication Summary"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("ZKP Round-wise Time Performance")
    if st.session_state.last_round_times is not None:
        count = st.session_state.last_rounds_count
        labels = [f"Round {i+1}" for i in range(count)]
        df = pd.DataFrame({
            "Round": labels,
            "Time (seconds)": st.session_state.last_round_times
        })
        fig3 = px.bar(df, x="Round", y="Time (seconds)", title=f"Time Taken per Round ({count} rounds)")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Perform a successful login first to see round-wise time performance.")

    st.subheader("Recent Failed Login Attempts")
    recent = analytics.get_recent_failures(limit=10)
    if recent:
        recent_df = pd.DataFrame(recent)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.write("No failed attempts recorded yet.")

st.caption("Image Authentication System - Privacy-Preserving Zero-Knowledge Proof for Hospital Patient Portal")