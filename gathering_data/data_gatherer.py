from gathering_data.classes import *
from gathering_data.util import *
import requests
import pandas as pd
from dotenv import load_dotenv
import os

import config

load_dotenv()


class NaverRECrawler:
    """Resolve a location to coordinates and collect nearby real-estate data."""

    def __init__(self) -> None:
        self.default_coordinates = config.DEFAULT_COORDINATES
        self.api_key = os.getenv(config.ENV_GOOGLE_API_KEY)

    def get_coordinates(self, query: str) -> NLocation:
        """Geocode ``query`` via Google Maps, falling back to known coordinates."""
        try:
            response = requests.get(
                config.GOOGLE_GEOCODE_URL,
                params={"address": query, "key": self.api_key},
            )
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK" and data["results"]:
                    location = data["results"][0]["geometry"]["location"]
                    return NLocation(float(location["lat"]), float(location["lng"]))
        except Exception as e:
            print(f"API Error: {str(e)}")

        if query in self.default_coordinates:
            return NLocation(*self.default_coordinates[query])

        raise Exception(f"Location not found for: {query}")

    def search_location(self, query: str) -> pd.DataFrame:
        """Return a dataframe of properties around the geocoded ``query``."""
        location = self.get_coordinates(query)
        print(f"Searching around coordinates: {location}")
        sector = get_sector(location)
        return self._get_real_estate_data(sector)

    def _get_real_estate_data(self, sector) -> pd.DataFrame:
        """Build the property dataframe for ``sector`` with prices normalised."""
        things = get_things_each_direction(sector)
        neighbors = get_all_neighbors(sector)
        update_things_intersection(things, neighbors, get_distance_standard())
        df = pd.DataFrame([t.get_list() for t in things], columns=NThing.HEADER)

        # Convert price units from 만원 (10k KRW) to 억원 (100M KRW).
        for col in config.PRICE_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: round(x / config.PRICE_UNIT_DIVISOR, config.PRICE_DECIMALS)
                    if pd.notnull(x) else x
                )

        return df


if __name__ == "__main__":
    crawler = NaverRECrawler()
    try:
        location = input("검색할 위치를 입력하세요 (예: 강남역): ")
        df = crawler.search_location(location)

        print(f"\n총 {len(df)}개의 매물이 검색되었습니다.")
        columns_to_show = [
            "Name",
            "Type",
            "Build",
            "minDeal",
            "maxDeal",
            "representativeArea",
        ]
        print(df[columns_to_show].head())

        output_file = f"{location}_real_estate_data.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n데이터가 {output_file}로 저장되었습니다.")
    except Exception as e:
        print(f"Error: {str(e)}")