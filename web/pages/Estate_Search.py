import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Ensure the project root is importable so the data / analysis packages resolve.
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config
from analysis.PandasAI_Analysis import run, format_analysis_results, clean_property_dataframe
from gathering_data.util import extract_location_from_query

load_dotenv()

# Streamlit configuration
st.set_page_config(page_title="Korea Real Estate Search", layout="centered")

# Selectable locations shown in the "Predefined Questions" flow, mapped to the
# English name passed to the geocoder / analysis layer.
LOCATIONS = [
    "Gangnam Station(강남역)",
    "Seoul Station(서울역)",
    "Hangang Park(한강공원)",
    "Hongdae Station(홍대입구역)",
    "Itaewon Station(이태원역)",
    "Busan Station(부산역)",
    "Daejeon Station(대전역)",
]
LOCATION_MAPPING = {
    "Gangnam Station(강남역)": "Gangnam Station",
    "Seoul Station(서울역)": "Seoul Station",
    "Hangang Park(한강공원)": "Hangang Park",
    "Hongdae Station(홍대입구역)": "Hongdae Station",
    "Itaewon Station(이태원역)": "Itaewon Station",
    "Busan Station(부산역)": "Busan Station",
    "Daejeon Station(대전역)": "Daejeon Station",
}

# Ready-made questions grouped by category for the "Predefined Questions" flow.
PREDEFINED_QUERIES = {
    "Price-related": [
        "Find properties priced below 300 million KRW",
        "Top 3 properties with the lowest monthly rent",
        "Properties with the lowest price per square meter",
    ],
    "Area/Structure-related": [
        "Recommend properties that are south-facing and have a large area",
        "List of properties with an area of 20 pyeong or more",
        "Show only properties with parking spaces",
    ],
    "Building Condition": [
        "Show buildings constructed after 2010",
        "Find remodeled properties",
        "Recommend properties in good maintenance condition",
    ],
}


def initialize_session_state() -> None:
    """Seed the session-state keys used by the search page."""
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "current_data" not in st.session_state:
        st.session_state.current_data = None


def main() -> None:
    initialize_session_state()

    st.title("🏢 Korea Real Estate Search")

    # Query input method selection
    query_method = st.radio(
        "Choose Search Method",
        ["Predefined Questions", "Direct Input"]
    )

    search_query = ""

    if "Direct" in query_method:
        search_query = st.text_input(
            "Enter your question",
            placeholder="Refer to the example below"
        )

        st.markdown(
            '<small style="color: grey;">Example: Find a house under 300 million won near gangnam<br>'
            'If no specific location is mentioned, the search will default to all of Seoul.</small>',
            unsafe_allow_html=True
        )

    else:
        # Location selector
        selected_location = st.selectbox(
            "Select Location",
            LOCATIONS
        )
        selected_location_eng = LOCATION_MAPPING[selected_location]

        # Category selection
        category = st.selectbox(
            "Select Category",
            list(PREDEFINED_QUERIES.keys())
        )

        # Query selection from category
        if category:
            search_query = st.selectbox(
                "Select Question",
                PREDEFINED_QUERIES[category]
            )

    if st.button("Search"):
        if search_query:
            with st.spinner("Analyzing data..."):
                try:
                    # For direct input, auto-extract the location from the query.
                    if "Direct" in query_method:
                        selected_location = extract_location_from_query(search_query)
                        selected_location_eng = selected_location

                    # Run the analysis
                    contextualized_query = f"{selected_location} ({selected_location_eng}): {search_query}"
                    df, query_result = run(contextualized_query, "openai", location=selected_location)

                    if df is not None:
                        # Deduplicate and drop zero-priced rows before display.
                        df_cleaned = clean_property_dataframe(df)

                        formatted_result = format_analysis_results(df_cleaned, query_result)

                        # Display results
                        st.success("Search completed.")
                        st.markdown("### **📊 Analysis Summary**")
                        st.markdown(
                            '<small>Selected Location<br>'
                            f'**{selected_location}**</small>',
                            unsafe_allow_html=True
                        )

                        # Summary statistics
                        stats = formatted_result["stats"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Properties", f"{stats['Total Properties']:,}")
                        with col2:
                            st.metric("Unique Buildings", f"{stats['Unique Buildings']:,}")
                        with col3:
                            st.metric("Average Area", f"{stats['Average Area']:.1f}㎡")

                        # OpenAI analysis result
                        st.markdown("### **Analysis Results**")
                        st.dataframe(df_cleaned[:config.MAX_DISPLAY_ROWS], hide_index=True)

                        # Highest priced properties
                        st.markdown("### **Top 5 Highest Priced Properties**")
                        st.dataframe(formatted_result["top_properties"], hide_index=True)

                        # Most affordable properties
                        st.markdown("### **Top 5 Affordable Properties**")
                        st.dataframe(formatted_result["affordable_properties"], hide_index=True)

                    else:
                        st.error("There are no results for the property you're looking for")

                except Exception as e:
                    st.error(f"An error occurred during search: {str(e)}")

    # Footer with instructions
    st.markdown("---")
    st.markdown("""
    **Search Tips:**
    - Enter specific details about what you're looking for
    - You can mention price range, preferred area, building condition, etc.
    - Use predefined questions for common queries
    """)


if __name__ == "__main__":
    main()
