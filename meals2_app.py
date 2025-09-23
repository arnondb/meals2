import streamlit as st

# --- Hardcoded credentials ---
users = {
    "alice": "password123",
    "bob": "secret456"
}

# --- Session state initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("Login Page")

# --- Login form ---
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# --- Main content if logged in ---
if st.session_state.logged_in:
    st.write("### Hello world")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
