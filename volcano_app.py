import pandas as pd
import streamlit as st
import pydeck as pdk

# 🌋 Page setup
st.set_page_config(page_title="🌋 Volcano Explorer", page_icon="🌋")

st.title("🌋 Volcano Explorer")
st.markdown("Upload your volcano dataset to begin exploring.")
uploaded_file = st.file_uploader("Drag and drop your `VOLCANOES DATA.csv` file here 👇", type="csv")

if uploaded_file is not None:
    # Load and clean the data
    df = pd.read_csv(uploaded_file)
    df = df.dropna(subset=['Latitude', 'Longitude', 'Country', 'Elevation (Meters)'])

    # Sidebar filters
    country = st.sidebar.selectbox("Select a country:", sorted(df['Country'].unique()))
    min_elev, max_elev = st.sidebar.slider("Elevation Range (meters):",
                                           int(df["Elevation (Meters)"].min()),
                                           int(df["Elevation (Meters)"].max()),
                                           (0, 5000))

    # Filtered data
    filtered_df = df[(df["Country"] == country) &
                     (df["Elevation (Meters)"] >= min_elev) &
                     (df["Elevation (Meters)"] <= max_elev)]

    st.subheader("Filtered Volcanoes")
    st.dataframe(filtered_df[['Volcano Name', 'Country', 'Type', 'Elevation (Meters)', 'Latitude', 'Longitude']])

    st.subheader("Top 5 Tallest Volcanoes")
    top5 = filtered_df.sort_values("Elevation (Meters)", ascending=False).head(5)
    st.bar_chart(top5.set_index("Volcano Name")["Elevation (Meters)"])

    st.subheader("Map of Volcano Locations")
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=filtered_df["Latitude"].mean(),
            longitude=filtered_df["Longitude"].mean(),
            zoom=3.5,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_df,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=10000,
            ),
        ],
    ))

    # Count volcanoes and show animation
    total = len(filtered_df)
    st.success(f"Found {total} volcanoes in {country}!")
    if total >= 10:
        st.balloons()
    elif total == 0:
        st.warning("No volcanoes found in that range.")
        st.snow()
else:
    st.info("Please upload a CSV file to get started.")
