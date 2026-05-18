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
# BUILD DEFAULT POINT SYSTEMS PER COMPETITION
# -------------------------------------------------
default_point_systems = []

for comp in range(DEFAULT_COMPETITIONS):
    comp_points = {}
    for rank, values in default_points.items():
        if comp < len(values):
            comp_points[rank] = values[comp]
        else:
            comp_points[rank] = 0
    default_point_systems.append(comp_points)

# -------------------------------------------------
# SCORING SYSTEMS (FIXED)
# -------------------------------------------------
st.sidebar.header("Scoring Systems")

point_systems = []

for comp in range(num_competitions):
    with st.sidebar.expander(f"{competition_names[comp]} Scoring", expanded=False):
        points = {}

        for r in range(0, num_ranks + 1):

            # ✅ Use correct default per competition
            if comp < len(default_point_systems):
                default_val = default_point_systems[comp].get(r, 0)
            else:
                default_val = 0

            points[r] = st.number_input(
                f"Rank {r}",
                min_value=0,
                max_value=100,
                value=int(default_val),
                key=f"comp{comp}_rank{r}_v2"  # ✅ changed key to avoid stale cache
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
    (df["Total Points"] >= min_points) &
    (df["Total Points"] <= max_points)
]

# Rank filters
for i in range(num_competitions):
    selected = st.sidebar.multiselect(
        f"{competition_names[i]} Rank",
        options=list(range(0, num_ranks + 1)),
        key=f"filter_{i}"
    )

    if selected:
        filtered_df = filtered_df[
            filtered_df[f"{competition_names[i]} Rank"].isin(selected)
        ]

# -------------------------------------------------
# TABLE DISPLAY
# -------------------------------------------------
st.subheader("Results")

sort_col = st.selectbox("Sort by", filtered_df.columns)
ascending = st.checkbox("Ascending", False)

filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

st.dataframe(filtered_df, use_container_width=True)

# -------------------------------------------------
# SUMMARY
# -------------------------------------------------
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Combinations", len(filtered_df))
col2.metric("Max points", filtered_df["Total Points"].max() if not filtered_df.empty else 0)
col3.metric("Min points", filtered_df["Total Points"].min() if not filtered_df.empty else 0)

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
csv = filtered_df.to_csv(index=False)
st.download_button("📥 Download CSV", csv, "results.csv")

# -------------------------------------------------
# PERFORMANCE WARNING
# -------------------------------------------------
if (num_ranks + 1) ** num_competitions > 50000:
    st.warning("⚠️ Large dataset — may be slow.")
