import itertools
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("🏆 Multi-Competition Ranking Analyzer")

# ----------------------------
# GLOBAL SETTINGS
# ----------------------------
st.sidebar.header("Configuration")

num_competitions = st.sidebar.number_input(
    "Number of competitions", min_value=1, max_value=6, value=3
)

num_ranks = st.sidebar.slider(
    "Number of ranking positions", min_value=2, max_value=20, value=15
)

# ----------------------------
# BUILD SCORING SYSTEMS
# ----------------------------
st.sidebar.header("Scoring Systems")

point_systems = []

for comp in range(num_competitions):
    with st.sidebar.expander(f"Competition {comp+1} Scoring", expanded=False):
        points = {}
        for r in range(1, num_ranks + 1):
            default_val = max(num_ranks - r + 1, 0)  # simple default
            points[r] = st.number_input(
                f"Rank {r} points (Comp {comp+1})",
                min_value=0,
                max_value=100,
                value=default_val,
                key=f"comp{comp}_rank{r}"
            )
        point_systems.append(points)

# ----------------------------
# GENERATE COMBINATIONS
# ----------------------------
@st.cache_data
def generate_data(num_competitions, num_ranks, point_systems):
    combinations = list(
        itertools.product(range(1, num_ranks + 1), repeat=num_competitions)
    )

    data = []

    for combo in combinations:
        row = {}
        total = 0

        for i in range(num_competitions):
            rank = combo[i]
            points = point_systems[i].get(rank, 0)

            row[f"Comp{i+1} Rank"] = rank
            row[f"Comp{i+1} Points"] = points

            total += points

        row["Total Points"] = total
        data.append(row)

    return pd.DataFrame(data)


df = generate_data(num_competitions, num_ranks, point_systems)

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("Filters")

min_points = st.sidebar.number_input("Min total points", 0, 1000, 0)
max_points = st.sidebar.number_input("Max total points", 0, 1000, 1000)

filtered_df = df[
    (df["Total Points"] >= min_points) &
    (df["Total Points"] <= max_points)
]

# Rank filters dynamically
for i in range(num_competitions):
    selected = st.sidebar.multiselect(
        f"Comp{i+1} Rank filter",
        options=list(range(1, num_ranks + 1)),
        key=f"filter_comp{i}"
    )

    if selected:
        filtered_df = filtered_df[
            filtered_df[f"Comp{i+1} Rank"].isin(selected)
        ]

# ----------------------------
# SORTING
# ----------------------------
st.subheader("Results")

sort_col = st.selectbox("Sort by", filtered_df.columns)
ascending = st.checkbox("Ascending", value=False)

filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

st.dataframe(filtered_df, use_container_width=True)

# ----------------------------
# SUMMARY
# ----------------------------
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total combinations", len(filtered_df))
col2.metric("Max points", filtered_df["Total Points"].max() if not filtered_df.empty else 0)
col3.metric("Min points", filtered_df["Total Points"].min() if not filtered_df.empty else 0)

# ----------------------------
# DOWNLOAD
# ----------------------------
csv = filtered_df.to_csv(index=False)
st.download_button("📥 Download CSV", csv, "ranking_results.csv")

# ----------------------------
# PERFORMANCE WARNING
# ----------------------------
if num_ranks ** num_competitions > 50000:
    st.warning("⚠️ Large dataset — may be slow. Consider reducing size.")
