import streamlit as st
from pathlib import Path
import db_manager

st.set_page_config(layout="wide")

db_path = "userdatabase/user_db.sqlite"  # Path to your database

# Check if the database exists, create it if not
db_manager.create_database(db_path)
db_manager.create_table(db_path)

# URL parameter handling
params = st.query_params
is_signup = params.get("signup", "false").lower() == "true"

# Ensure session state is initialized
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Toggle between login and signup
if not is_signup and not st.session_state["authenticated"]:
    st.header("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if db_manager.verify_user(db_path, username, password):
            st.success(f"Logged in as {username}")
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # ✅ Store username in session
            st.rerun()
        else:
            st.error("Incorrect username or password")

    st.markdown("[Sign Up Here](?signup=true)")
elif is_signup and not st.session_state["authenticated"]:
    st.header("Sign Up")
    signup_username = st.text_input("Username")
    signup_password = st.text_input("Password", type="password")
    signup_password_confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if signup_password == signup_password_confirm:
            if db_manager.add_user(db_path, signup_username, signup_password):
                st.success("Signup successful! You can now log in.")
                st.query_params["signup"] = "false"
                st.rerun()
            else:
                st.error("Username already exists.")
        else:
            st.error("Passwords do not match.")

    st.markdown("[Back to Login](?signup=false)")

# Authenticated user session
if st.session_state["authenticated"]:
    if st.session_state["authenticated"]:
        st.header(
            f"Welcome, {st.session_state.get('username', 'User')}!"
        )  # ✅ Show logged-in username

    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None  # ✅ Clear username on logout
        st.rerun()
    # st.header("Welcome!")
    about_page = st.Page(
        "views/about_me.py",
        title="About Me",
        icon=":material/account_circle:",
        default=True,
    )
    project_1_page = st.Page(
        "views/SchoolDashboard.py",
        title="Students Data Dashboard",
        icon=":material/bar_chart:",
    )
    project_2_page = st.Page(
        "views/chatbot.py",
        title="Chat Bot",
        icon=":material/smart_toy:",
    )
    if st.session_state["username"] == "admin":
        project_3_page = st.Page(
            "views/secret.py",
            title="File Uploading",
            icon=":material/upload_file:",
        )
        projects = [project_1_page, project_2_page, project_3_page]
    else:
        projects = [project_2_page]
    pg = st.navigation(
        {
            "Info": [about_page],
            "Projects": projects,
        }
    )
    selected_page = pg.run()  # Run navigation and get the active page

    if selected_page and selected_page.title == "Secret":
        if st.session_state["username"] != "admin":
            st.error("You are not authorized to access this page.")
            st.stop()
    st.sidebar.markdown("made by doui")
