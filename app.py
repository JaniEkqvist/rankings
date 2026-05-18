import itertools
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("🏆 Multi-Competition Ranking Analyzer")

st.info("Rank 0 = Did not participate / no valid result")

# -------------------------------------------------
# DEFAULT DATA (YOUR TABLE)
# -------------------------------------------------
default_names = ["Vätsäri", "Karjala", "Etelä"]

default_points = {
    0: [0, 0, 0],
    1: [50, 30, 20],
    2: [40, 24, 16],
    3: [36, 22, 14],
    4: [32, 19, 13],
    5: [27, 16, 11],
    6: [24, 14, 10],
    7: [21, 12, 9],
    8: [18, 10, 8],
    9: [15, 8, 7],
    10: [13, 7, 6],
    11: [11, 6, 5],
    12: [9, 5, 4],
    13: [7, 4, 3],
    14: [5, 3, 2],
    15: [3, 2, 1],
}

DEFAULT_RANKS = max(default_points.keys())
DEFAULT_COMPETITIONS = len(default_names)

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.sidebar.header("Configuration")

num_competitions = st.sidebar.number_input(
    "Number of competitions", min_value=1, max_value=6, value=DEFAULT_COMPETITIONS
)

num_ranks = st.sidebar.slider(
    "Max ranking", min_value=1, max_value=20, value=DEFAULT_RANKS
)

# -------------------------------------------------
# COMPETITION NAMES (EDITABLE)
# -------------------------------------------------
st.sidebar.header("Competition Names")

competition_names = []
for i in range(num_competitions):
    default_name = default_names[i] if i < len(default_names) else f"Comp{i+1}"
    name = st.sidebar.text_input(f"Competition {i+1} name", default_name, key=f"name{i}")
    competition_names.append(name)

# -------------------------------------------------
# SCORING SYSTEMS
# -------------------------------------------------
st.sidebar.header("Scoring Systems")

point_systems = []

for comp in range(num_competitions):
    with st.sidebar.expander(f"{competition_names[comp]} Scoring", expanded=False):
        points = {}

        for r in range(0, num_ranks + 1):
            # Load default if available
            default_val = 0
            if r in default_points and comp < len(default_points[r]):
                default_val = default_points[r][comp]

            points[r] = st.number_input(
                f"Rank {r}",
                min_value=0,
                max_value=100,
                value=default_val,
                key=f"comp{comp}_rank{r}"
            )

        point_systems.append(points)

# -------------------------------------------------
# DATA GENERATION
# -------------------------------------------------
@st.cache_data
def generate_data(num_competitions, num_ranks, point_systems, competition_names):
    combinations = list(
        itertools.product(range(0, num_ranks + 1), repeat=num_competitions)
    )

    data = []

    for combo in combinations:
        row = {}
        total = 0

        for i in range(num_competitions):
            rank = combo[i]
            pts = point_systems[i].get(rank, 0)

            row[f"{competition_names[i]} Rank"] = rank
            row[f"{competition_names[i]} Points"] = pts

            total += pts

        row["Total Points"] = total
        data.append(row)

    return pd.DataFrame(data)


df = generate_data(num_competitions, num_ranks, point_systems, competition_names)

# -------------------------------------------------
# FILTERS
# -------------------------------------------------
st.sidebar.header("Filters")

min_points = st.sidebar.number_input("Min total points", 0, 2000, 0)
max_points = st.sidebar.number_input("Max total points", 0, 2000, 2000)

filtered_df = df[
