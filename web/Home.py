import streamlit as st
from PIL import Image


def main():
    # Set page configuration
    st.set_page_config(
        page_title="K-RealEstate AI Search System",
        page_icon="🏠",
        layout="wide"
    )

    # Custom CSS to ensure consistent spacing and styling
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .element-container {
            margin-bottom: 1rem;
        }
        .stExpander {
            border: none !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
            margin-bottom: 1rem !important;
        }
        .mission-text {
            font-size: 1.2rem;
            line-height: 1.8;
            text-align: left;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)


    # Main content
    st.title("K-RealEstate AI Search System")
    st.subheader("Intelligent Korean Real Estate Search Platform")
    st.markdown("---")

    # Our Mission - Enhanced presentation
    with st.expander("🎯 Our Mission", expanded=True):
        st.markdown("""
            <div class="mission-text">
                Enhancing real estate search with natural language processing.<br>
                Simply describe your ideal home in your own words.<br>
                Let AI understand your needs and preferences.<br>
                Find your perfect property faster than ever.
            </div>
        """, unsafe_allow_html=True)

    # Technology Stack and Data Sources in two columns
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🛠 Technology Stack", expanded=True):
            st.markdown("""
                - Streamlit (Web Framework)
                - Crawl4AI (Data Collection)
                - OpenAI API (NLP Engine)
                - PandasAI (Data Analysis)
            """)
    with col2:
        with st.expander("📊 Data Sources", expanded=True):
            st.markdown("""
                - [Naver Real Estate](https://land.naver.com/)
            """)

    # How It Works section - Framework-focused descriptions
    st.markdown("---")
    st.markdown("### How It Works")
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("1. Data Collection", expanded=True):
            st.markdown("""
                - Streamlit-powered web scraping
                - Automated Naver Real Estate data collection
            """)

    with col2:
        with st.expander("2. AI Processing", expanded=True):
            st.markdown("""
                - OpenAI API natural language processing
                - PandasAI-driven data analysis
            """)

    with col3:
        with st.expander("3. User Interface", expanded=True):
            st.markdown("""
                - Streamlit interactive components
                - Real-time search results
            """)

    # Call-to-action with better spacing
    st.markdown("---")
    st.markdown("### Ready to explore Korean real estate data?")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start Searching 🔍", width="stretch", type="primary"):
            st.switch_page("pages/Estate_Search.py")

if __name__ == "__main__":
    main()
