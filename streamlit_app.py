import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Pitch Tracker", page_icon="⚾")

# ======================
# DATABASE CONNECTION
# ======================
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("⚾ Pitch Tracker App")

# ======================
# DASHBOARD
# ======================
st.header("Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM pitches;")
    total_pitches = cur.fetchone()[0]

    cur.execute("SELECT AVG(velocity) FROM pitches;")
    avg_velo = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM pitchers;")
    total_pitchers = cur.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pitches", total_pitches)
    col2.metric("Avg Velocity", round(avg_velo, 1))
    col3.metric("Pitchers", total_pitchers)

    cur.close()
    conn.close()

except:
    st.warning("Database not connected yet")

st.markdown("---")

# ======================
# ADD PITCHER
# ======================
st.header("Add Pitcher")

with st.form("pitcher_form"):
    name = st.text_input("Pitcher Name")
    team = st.text_input("Team")
    submit_pitcher = st.form_submit_button("Add Pitcher")

    if submit_pitcher:
        if name.strip():
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO pitchers (name, team) VALUES (%s, %s);",
                    (name, team)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Pitcher added!")
            except Exception as e:
                st.error(e)
        else:
            st.warning("Name is required")

st.markdown("---")

# ======================
# ADD PITCH
# ======================
st.header("Add Pitch")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM pitchers ORDER BY name;")
    pitchers = cur.fetchall()
    cur.close()
    conn.close()

    if pitchers:
        pitcher_dict = {p[1]: p[0] for p in pitchers}

        with st.form("pitch_form"):
            pitcher_name = st.selectbox("Pitcher", pitcher_dict.keys())
            pitch_type = st.selectbox("Pitch Type", ["Fastball", "Slider", "Curveball", "Changeup"])
            velocity = st.number_input("Velocity (mph)", min_value=0, max_value=110)
            result = st.selectbox("Result", ["Strike", "Ball", "Hit", "Foul"])
            submit_pitch = st.form_submit_button("Add Pitch")

            if submit_pitch:
                if velocity > 0:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO pitches (pitcher_id, pitch_type, velocity, result) VALUES (%s, %s, %s, %s);",
                            (pitcher_dict[pitcher_name], pitch_type, velocity, result)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("Pitch added!")
                    except Exception as e:
                        st.error(e)
                else:
                    st.warning("Velocity must be greater than 0")

    else:
        st.warning("Add a pitcher first")

except:
    st.error("Error loading pitchers")

st.markdown("---")

# ======================
# VIEW + SEARCH
# ======================
st.header("Pitch Data")

search = st.text_input("Search by pitch type")

try:
    conn = get_connection()
    cur = conn.cursor()

    if search.strip():
        cur.execute(
            """
            SELECT p.id, p.pitch_type, p.velocity, p.result, pi.name
            FROM pitches p
            JOIN pitchers pi ON p.pitcher_id = pi.id
            WHERE p.pitch_type ILIKE %s;
            """,
            (f"%{search}%",)
        )
    else:
        cur.execute(
            """
            SELECT p.id, p.pitch_type, p.velocity, p.result, pi.name
            FROM pitches p
            JOIN pitchers pi ON p.pitcher_id = pi.id;
            """
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Type", "Velocity", "Result", "Pitcher"])
        st.dataframe(df)

        # ======================
        # DELETE
        # ======================
        st.subheader("Delete Pitch")

        delete_id = st.number_input("Enter Pitch ID to delete", min_value=1)

        if st.button("Delete Pitch"):
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM pitches WHERE id = %s;", (delete_id,))
                conn.commit()
                cur.close()
                conn.close()
                st.success("Pitch deleted!")
            except Exception as e:
                st.error(e)

    else:
        st.info("No pitches yet")

except:
    st.error("Error loading data")