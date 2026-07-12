"""Central configuration for the K-RealEstate AI Search System.

All non-secret constants (API endpoints, model names, region codes, magic
numbers and prompt templates) live here so they can be tuned in one place and
never duplicated across modules.  Secrets (API keys) are always read from the
environment via the variable names defined below and are never hardcoded.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Environment variable names (values are loaded from the environment / .env)
# ---------------------------------------------------------------------------
ENV_OPENAI_API_KEY: str = "OPENAI_API_KEY"
ENV_GOOGLE_API_KEY: str = "GOOGLE_API_KEY"

# ---------------------------------------------------------------------------
# Large Language Model (OpenAI / PandasAI) settings
# ---------------------------------------------------------------------------
OPENAI_MODEL: str = "gpt-4o"
LOCATION_EXTRACTION_TEMPERATURE: float = 0.0
DEFAULT_LOCATION_FALLBACK: str = "Seoul"

PANDASAI_VERBOSE: bool = True
PANDASAI_ENABLE_CACHE: bool = True

# ---------------------------------------------------------------------------
# External API endpoints
# ---------------------------------------------------------------------------
NAVER_API_BASE_URL: str = "https://new.land.naver.com/api/"
GOOGLE_GEOCODE_URL: str = "https://maps.googleapis.com/maps/api/geocode/json"

# Emit request logging for the Naver public-data API.
NAVER_API_LOGGING: bool = True

# ---------------------------------------------------------------------------
# Naver real-estate search parameters
# ---------------------------------------------------------------------------
# Default "root" region code used when listing administrative regions.
DEFAULT_REGION_CODE: str = "0000000000"

# Inclusive bounds applied to the price / area filters of a marker search.
SEARCH_FILTER_MIN: int = 0
SEARCH_FILTER_MAX: int = 900_000_000

# ---------------------------------------------------------------------------
# Price normalisation (Korean won: 만원 -> 억원)
# ---------------------------------------------------------------------------
PRICE_UNIT_DIVISOR: int = 10_000
PRICE_DECIMALS: int = 2
PRICE_COLUMNS: list[str] = [
    "minDeal",
    "maxDeal",
    "medianDeal",
    "minLease",
    "maxLease",
    "medianLease",
]

# ---------------------------------------------------------------------------
# Fallback geocoding coordinates (lat, lon) used when the Google Geocoding
# API is unavailable for a well-known station name.
# ---------------------------------------------------------------------------
DEFAULT_COORDINATES: dict[str, tuple[float, float]] = {
    "강남역": (37.4979462, 127.0276206),
    "역삼역": (37.5006, 127.0368),
    "선릉역": (37.5044, 127.0505),
}

# ---------------------------------------------------------------------------
# Proximity thresholds (metres) used to count nearby amenities per property.
# ---------------------------------------------------------------------------
DEFAULT_DISTANCE_STANDARDS: dict[str, int] = {
    "BUS": 500,
    "METRO": 500,
    "INFANT": 750,
    "PRESCHOOL": 750,
    "PRI_SCHOOL": 1000,
    "PUB_SCHOOL": 1000,
    "HOSPITAL": 2000,
    "PARKING": 500,
    "MART": 500,
    "CONVENIENCE": 300,
    "WASHING": 500,
    "BANK": 750,
    "OFFICE": 1250,
}

# ---------------------------------------------------------------------------
# Analysis / presentation
# ---------------------------------------------------------------------------
# Maps the raw crawler columns to the friendly names used by the analysis and
# UI layers.
PROPERTY_COLUMN_MAPPING: dict[str, str] = {
    "Name": "Name",
    "minDeal": "MinPrice",
    "maxDeal": "MaxPrice",
    "representativeArea": "Area",
    "Type": "PropertyType",
}

# Number of rows / properties shown in result tables.
MAX_DISPLAY_ROWS: int = 20
TOP_N_PROPERTIES: int = 5

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
# Instruction sent to PandasAI to analyse the property dataframe. ``{query}``
# is substituted with the contextualised user query at call time.
PANDASAI_ANALYSIS_PROMPT_TEMPLATE: str = """
Analyze the real estate data for the following query: {query}

Return a dictionary with the following structure:
{{
    "type": "string",
    "value": "<your analysis here>"
}}

Include in your analysis:
1. A brief summary of findings
2. Specific insights related to the query
3. Notable properties that match the criteria
"""

# System prompt used to extract a single map-friendly location name from a
# free-text query.
LOCATION_EXTRACTION_SYSTEM_PROMPT: str = (
    "You are tasked with extracting the most specific location name mentioned in the user's query. "
    "The location must be returned as a single neighborhood or district name in English, suitable for use with Google Maps. "
    "Examples:\n"
    "- Input: 'Find a house under 300 million won near Hongik University' -> Output: 'Seogyo-dong'\n"
    "- Input: 'Recommend properties south-facing and large area near Hongik University' -> Output: 'Seogyo-dong'\n"
    "- Input: 'Apartments in Gangnam station' -> Output: 'Gangnam station'\n"
    "- Input: 'Properties near Itaewon' -> Output: 'Itaewon'\n"
)
