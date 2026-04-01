import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pitch Tracker", page_icon="⚾")

st.title("⚾ Baseball Pitch Tracker")

# Initialize session state
if "pitches" not in st.session_state:
    st.session_state.pitches = []

st.header("Add a Pitch")

with st.form("pitch_form"):
    pitch_type = st.selectbox("Pitch Type", ["Fastball", "Curveball", "Slider", "Changeup"])
    velocity = st.number_input("Velocity (mph)", min_value=0, max_value=110)
    result = st.selectbox("Result", ["Strike", "Ball", "Hit", "Foul"])
    submitted = st.form_submit_button("Add Pitch")

    if submitted:
        st.session_state.pitches.append({
            "Pitch Type": pitch_type,
            "Velocity": velocity,
            "Result": result
        })
        st.success("Pitch added!")

# Display data
st.header("Pitch Data")

if st.session_state.pitches:
    df = pd.DataFrame(st.session_state.pitches)
    st.dataframe(df)

    st.subheader("Stats")

    avg_velo = df["Velocity"].mean()
    st.write(f"Average Velocity: {avg_velo:.1f} mph")

    st.write("Pitch Type Counts:")
    st.write(df["Pitch Type"].value_counts())

    st.write("Results Breakdown:")
    st.write(df["Result"].value_counts())

else:
    st.info("No pitches recorded yet.")