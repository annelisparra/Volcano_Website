import pandas as pd  # data handling (input dataset)
import streamlit as st  # balloons and snow
import pydeck as pdk  # for map
import matplotlib.pyplot as plt  # for charts

# [ST4] Setting up page
st.set_page_config(page_title="🌋 Volcano Explorer", page_icon="🌋")

st.title("🌋 Volcano Explorer")
# [ST4] Add image
st.image("volcano.jpg", width=500, caption="Volcanoes of the World")
st.markdown("Upload your volcano dataset to begin exploring.")

# [ST1] File uploader
uploaded_file = st.file_uploader("Drag and drop your `VOLCANOES DATA.csv` file here 👇", type="csv")

if uploaded_file is not None:
    # 1️⃣ Read CSV (with fallback encoding)
    try: # [ST2]
        df = pd.read_csv(uploaded_file, encoding='latin1')
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # 2️⃣ Clean your headers _before_ any subsetting or dropna
    df.columns = df.columns.str.strip()  # remove stray spaces
    df.rename(columns={"Elevation (m)": "Elevation (Meters)"}, inplace=True)

    # (Optional) debug: confirm those names really exist
    st.write("▶ CLEANED COLUMNS:", df.columns.tolist())

    # 3️⃣ Now slice out the exact columns you need (keep the brackets!)
    keep_cols = [
        'Volcano Name',
        'Country',
        'Primary Volcano Type',
        'Latitude',
        'Longitude',
        'Elevation (Meters)'
    ]
    df = df[keep_cols]

    # 4️⃣ Finally, drop any rows missing those exact names
    df = df.dropna(subset=[
        'Latitude',
        'Longitude',
        'Country',
        'Elevation (Meters)'
    ])

    # [ST2] Sidebar filters, implementing min and max
    st.sidebar.header("🌍 Filter Volcanoes")
    country = st.sidebar.selectbox("Select a country:", sorted(df['Country'].unique()))
    min_elev, max_elev = st.sidebar.slider(
        "Elevation range (meters):",
        int(df["Elevation (Meters)"].min()),
        int(df["Elevation (Meters)"].max()),
        (0, 5000)
    )

    # [DA4] [DA5] Filter by one and multiple conditions
    filtered_df = df[
        (df["Country"] == country) &
        (df["Elevation (Meters)"] >= min_elev) &
        (df["Elevation (Meters)"] <= max_elev)
    ]

    st.subheader(f"🌋 Volcanoes in {country} between {min_elev}–{max_elev} meters")
    st.dataframe(filtered_df)  # [VIZ3]

    # [PY2] Function that returns more than one value
    def get_min_max_elevation(data):
        min_val = data["Elevation (Meters)"].min()
        max_val = data["Elevation (Meters)"].max()
        return min_val, max_val

    # [PY2] Call the function and unpack two values
    min_elev_val, max_elev_val = get_min_max_elevation(filtered_df)
    st.write(f"🔻 Lowest elevation: {min_elev_val} meters")
    st.write(f"🔺 Highest elevation: {max_elev_val} meters")

    # [PY4] List comprehension to extract volcano names
    volcano_names = [name for name in filtered_df["Volcano Name"]]
    st.write(f"📝 Volcanoes matching filter: {', '.join(volcano_names)}")

    # [VIZ1] PIE CHART with title and legend
    if not filtered_df.empty:
        st.subheader("Volcano Type Distribution")
        volcano_counts = filtered_df['Primary Volcano Type'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))

        top_types = volcano_counts[volcano_counts > 5]
        others = volcano_counts[volcano_counts <= 5].sum()
        labels = top_types.index.tolist()
        sizes = top_types.values.tolist()
        if others > 0:
            labels.append("Other")
            sizes.append(others)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            textprops={'fontsize': 10, 'color': 'white'},
            startangle=90
        )

        ax.set_title("Distribution of Volcano Types", fontsize=16, color="darkred")
        ax.legend(labels, title="Volcano Types", loc="center left", bbox_to_anchor=(1, 0.5))
        ax.axis('equal')
        st.pyplot(fig)

    # [PY1] Function with default param [PY2] Returns value
    def get_top_volcanoes(data, n=5):
        return data.sort_values("Elevation (Meters)", ascending=False).head(n)

    # [DA2] [DA3] BAR CHART of tallest volcanoes
    st.subheader("Top 5 Tallest Volcanoes (in meters)")
    fig2, ax2 = plt.subplots()
    top5 = get_top_volcanoes(filtered_df)
    if not top5.empty:
        ax2.bar(top5["Volcano Name"], top5["Elevation (Meters)"], color='firebrick')
        ax2.set_title("Tallest Volcanoes in Selected Country", fontsize=16, color="darkgreen")
        ax2.set_xlabel("Volcano Name", fontsize=12)
        ax2.set_ylabel("Elevation (Meters)", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    # [MAP] INTERACTIVE MAP with tooltip
    st.subheader("Map of Volcano Locations")
    if not filtered_df.empty:
        filtered_df["tooltip"] = (
            "🌋 " + filtered_df["Volcano Name"] +
            "<br>⛰️ " + filtered_df["Elevation (Meters)"].astype(str) + " meters" +
            "<br>🌶️ " + filtered_df["Primary Volcano Type"]
        )

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=filtered_df["Latitude"].mean(),
                longitude=filtered_df["Longitude"].mean(),
                zoom=4,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered_df,
                    get_position='[Longitude, Latitude]',
                    get_color='[255, 0, 0, 160]',
                    get_radius=10000,
                    pickable=True,
                ),
            ],
            tooltip={"html": "{tooltip}", "style": {"fontSize": "12px"}}
        ))

    # [DA8] Iterate through rows with iterrows
    for _, row in filtered_df.iterrows():
        st.write(
            f"🌋 **{row['Volcano Name']}** | Type: {row['Primary Volcano Type']} | Elevation: {row['Elevation (Meters)']} m"
        )

    # Final animation feedback
    total = len(filtered_df)
    if total >= 10:
        st.success(f"You found {total} volcanoes!")
        st.balloons()
    elif total == 0:
        st.warning("No volcanoes match those filters. Try expanding the elevation range.")
        st.snow()
else:
    st.info("Please upload a CSV file to get started.")
