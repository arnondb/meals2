import streamlit as st
from datetime import datetime, date
import pandas as pd
from supabase import create_client

# --- Credentials ---
users = {"Efrat": "efchek123", "Arnon": "Aloniloni1"}

# --- Supabase ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "meals_data" not in st.session_state:
    st.session_state.meals_data = pd.DataFrame()

st.title("Meal Tracker")

# --- Login ---
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# --- App ---
if st.session_state.logged_in:
    st.subheader(f"Welcome, {st.session_state.username}!")

    # --- Add meal ---
    st.write("### Add a meal")
    meal_options = ["Bonty", "Shnitzl and rice", "Pita sandwich", "Pizza", "Pizza-Pita", "Cornflakes nad milk", "Other"]
    meal_type = st.selectbox("Meal type", meal_options)
    custom_meal = st.text_input("Or enter a custom meal type")

    # Date and time inputs
    now = datetime.now()
    meal_date = st.date_input("Meal date", now)
    hours = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    default_time = now.strftime("%H:%M")
    meal_time_str = st.selectbox("Meal time", options=hours, index=hours.index(default_time) if default_time in hours else 0)

    if st.button("Save meal"):
        chosen_meal = custom_meal if custom_meal else meal_type
        data = {
            "username": st.session_state.username,
            "meal_type": chosen_meal,
            "meal_time": meal_time_str,
            "meal_date": meal_date.strftime("%d/%m/%Y"),  # DD/MM/YYYY format
        }
        supabase.table("meals").insert(data).execute()
        st.toast("✅ Meal saved!")
        st.rerun()

    # --- Filter meals ---
    st.write("### Filter meals by date")
    start_date = st.date_input("Start date", date.today())
    end_date = st.date_input("End date", date.today())

    query = supabase.table("meals").select("*")
    if start_date:
        query = query.gte("meal_date", start_date.strftime("%d/%m/%Y"))
    if end_date:
        query = query.lte("meal_date", end_date.strftime("%d/%m/%Y"))
    meals = query.execute()

    if meals.data:
        df = pd.DataFrame(meals.data)
        df = df[["id", "meal_date", "meal_time", "meal_type", "username"]]

        # Format date for display
        df["meal_date"] = pd.to_datetime(df["meal_date"], dayfirst=True).dt.strftime("%d/%m/%Y")

        st.write("### All Meals")

        # Display table dynamically with buttons
        for idx, row in df.iterrows():
            cols = st.columns([1, 2, 2, 2, 2, 1])
            cols[0].write(row["id"])
            cols[1].write(row["meal_date"])
            cols[2].write(row["meal_time"])
            cols[3].write(row["meal_type"])
            cols[4].write(row["username"])
            if cols[5].button("Delete", key=f"delete-{row['id']}"):
                supabase.table("meals").delete().eq("id", row["id"]).execute()
                st.toast(f"🗑️ Meal ID {row['id']} deleted")
                st.rerun()

        # Responsive DataFrame below (sortable, scrollable)
        st.write("#### Full Table")
        st.dataframe(df.drop(columns=["id"]), use_container_width=True)

    else:
        st.info("No meals found for this date range.")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.meals_data = pd.DataFrame()
        st.rerun()
