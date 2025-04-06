import streamlit as st
import requests
import datetime
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Advanced Unit Converter", layout="centered")

# Custom CSS for beautification
st.markdown("""
    <style>
        html, body {
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1.5em;
        }
        .stDownloadButton>button {
            background-color: #1f77b4;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Theme toggle
with st.sidebar:
    st.title("⚙️ Settings")
    st.session_state.dark_mode = st.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)

# Apply theme
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            .stApp {
                background-color: #1e1e1e;
            }
        </style>
    """, unsafe_allow_html=True)

# App content
st.title("🔁 Advanced Unit Converter")
st.markdown("##### Instantly convert Length, Weight, Time, Temperature, and Currency")

# Main function
def convert_units(category, value, unit):
    if category == "Length":
        if unit == "Kilometer to miles":
            return value * 0.621371
        elif unit == "Miles to Kilometer":
            return value / 0.621371

    elif category == "Weight":
        if unit == "Kilogram to Pounds":
            return value * 2.20462
        elif unit == "Pounds to Kilogram":
            return value / 2.20462

    elif category == "Time":
        conversions = {
            "Seconds to Minutes": value / 60,
            "Minutes to Seconds": value * 60,
            "Minutes to hours": value / 60,
            "Hours to minutes": value * 60,
            "Hours to days": value / 24,
            "Days to hours": value * 24,
        }
        return conversions.get(unit, None)

    elif category == "Temperature":
        if unit == "Celsius to Fahrenheit":
            return (value * 9 / 5) + 32
        elif unit == "Fahrenheit to Celsius":
            return (value - 32) * 5 / 9
        elif unit == "Celsius to Kelvin":
            return value + 273.15
        elif unit == "Kelvin to Celsius":
            return value - 273.15

    elif category == "Currency":
        base, target = unit.split(" to ")
        url = f"https://api.exchangerate.host/latest?base={base}&symbols={target}"
        response = requests.get(url)
        if response.status_code == 200:
            rate = response.json()['rates'][target]
            return value * rate
        else:
            st.error("❌ Could not fetch live rates.")
            return None

# UI: Category Selection
category = st.selectbox("📂 Select Category", ["Length", "Weight", "Time", "Temperature", "Currency"])

# UI: Searchable Unit Selection (Replace dropdown with search)
units = {
    "Length": ["Kilometer to miles", "Miles to Kilometer"],
    "Weight": ["Kilogram to Pounds", "Pounds to Kilogram"],
    "Time": [
        "Seconds to Minutes", "Minutes to Seconds", "Minutes to hours",
        "Hours to minutes", "Hours to days", "Days to hours"
    ],
    "Temperature": ["Celsius to Fahrenheit", "Fahrenheit to Celsius", "Celsius to Kelvin", "Kelvin to Celsius"],
    "Currency": ["USD to PKR", "PKR to USD", "USD to EUR", "EUR to USD", "USD to GBP", "GBP to USD"]
}

unit = st.selectbox("Search and Select Conversion", units[category])

value = st.number_input("🔢 Enter the value to convert", min_value=0.0)

# Convert button
if st.button("🔄 Convert"):
    result = convert_units(category, value, unit)
    if result is not None:
        st.success(f"✅ Result: **{result:.2f}**")

        # Save to history
        record = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {value} → {result:.2f} | {unit} ({category})"
        st.session_state.history.append(record)

        # Download result only
        st.download_button("📥 Download Result", record, file_name="conversion_result.txt")

# History Viewer
if st.session_state.history:
    st.markdown("### 📜 Conversion History")
    for item in reversed(st.session_state.history):
        st.markdown(f"`{item}`")

    # Save full history
    history_data = "\n".join(st.session_state.history)
    st.download_button("🗂 Download Full History", history_data, file_name="conversion_history.txt")

    # Add chart for conversion history stats
    data = {"Category": [], "Count": []}
    for item in st.session_state.history:
        category = item.split("|")[2].split("(")[1][:-1]
        if category in data["Category"]:
            data["Count"][data["Category"].index(category)] += 1
        else:
            data["Category"].append(category)
            data["Count"].append(1)

    df = pd.DataFrame(data)
    fig = px.bar(df, x="Category", y="Count", title="Conversion History Stats")
    st.plotly_chart(fig)
