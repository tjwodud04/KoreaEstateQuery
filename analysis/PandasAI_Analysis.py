"""Business/LLM layer: turn raw crawler data into analysed, presentable results."""

import os
from typing import Optional

import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from dotenv import load_dotenv

import config
from gathering_data.data_gatherer import NaverRECrawler

load_dotenv()


def clean_property_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate buildings and zero-priced rows, then reset the index.

    Deduplicates on ``Name`` (keeping the first occurrence) and drops rows whose
    ``MaxPrice`` is 0, which represent listings without a valid deal price.
    """
    df_cleaned = df.drop_duplicates(subset="Name", keep="first")
    df_cleaned = df_cleaned[df_cleaned["MaxPrice"] != 0]
    return df_cleaned.reset_index(drop=True)


def format_analysis_results(df: pd.DataFrame, query_result: dict) -> dict:
    """Summarise ``df`` into stats plus top/affordable property tables."""
    try:
        stats = {
            "Total Properties": len(df),
            "Unique Buildings": df["Name"].nunique(),
            "Average Price": df["MinPrice"].mean(),
            "Average Area": df["Area"].mean(),
            "Price Range": (df["MinPrice"].min(), df["MaxPrice"].max()),
        }

        top_n = config.TOP_N_PROPERTIES
        result_columns = ["Name", "MinPrice", "MaxPrice", "Area"]
        return {
            "stats": stats,
            "top_properties": df.nlargest(top_n, "MaxPrice")[result_columns],
            "affordable_properties": df.nsmallest(top_n, "MinPrice")[result_columns],
            "query_result": query_result,
        }

    except Exception as e:
        return {"error": f"Formatting error: {str(e)}"}


def run(
    input_query: str,
    model: str,
    location: Optional[str] = None,
    data: Optional[pd.DataFrame] = None,
):
    """Fetch (if needed) and analyse real-estate data for ``input_query``.

    Returns a ``(dataframe, result_dict)`` tuple. On failure the dataframe is
    ``None`` and the result dict carries the error message.
    """
    try:
        # Data retrieval
        if data is None and location is not None:
            crawler = NaverRECrawler()
            data = crawler.search_location(location)
        elif data is None:
            raise ValueError("Either location or data must be provided")

        # Map raw crawler columns to the friendly analysis column names.
        column_mapping = config.PROPERTY_COLUMN_MAPPING
        df = data[list(column_mapping.keys())].copy()
        df.columns = list(column_mapping.values())

        # OpenAI model handling
        if model == "openai":
            openai_api_key = os.getenv(config.ENV_OPENAI_API_KEY)
            if not openai_api_key:
                raise ValueError("OpenAI API key not found")

            llm = OpenAI(api_token=openai_api_key, model_name=config.OPENAI_MODEL)
            sdf = SmartDataframe(df, config={
                "llm": llm,
                "verbose": config.PANDASAI_VERBOSE,
                "enable_cache": config.PANDASAI_ENABLE_CACHE,
            })

            prompt = config.PANDASAI_ANALYSIS_PROMPT_TEMPLATE.format(query=input_query)
            result = sdf.chat(prompt)

            # Ensure proper output format
            if isinstance(result, dict) and "type" in result and "value" in result:
                return df, result
            # Format the result if it's not already in the correct format
            return df, {"type": "string", "value": str(result)}

        return df, {"type": "string", "value": "Model not supported."}

    except Exception as e:
        return None, {"type": "error", "value": f"Error occurred: {str(e)}"}


if __name__ == "__main__":
    try:
        crawler = NaverRECrawler()
        location = input("Enter location to search (e.g., Gangnam Station): ")
        df = crawler.search_location(location)
        print(f"\nSuccessfully loaded data for {location}")

        while True:
            test_input = input("\nEnter your query (or 'q' to quit): ")
            if test_input.lower() == "q":
                break
            print("\nAnalyzing your query...")
            result = run(test_input, "openai", data=df)
            print(result)
    except Exception as e:
        print(f"Program error: {str(e)}")
