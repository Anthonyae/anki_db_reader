"""This module provides functions for querying the Anki database."""

import os
import platform
import re
import sqlite3

import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

ANKI_DB = os.getenv("ANKI_DB", "")

system_name = platform.system()
if "microsoft" in platform.uname().release.lower():
    drive, path = ANKI_DB.split(":", 1)
    ANKI_DB = r"/mnt/" + drive.lower() + path.replace("\\", "/")


def unicase_collation(s1, s2):
    """A utility function that provides collation for handling queries involving tables with non standard text in sqlite3."""
    return s1.lower() == s2.lower()


class AnkiDB:
    """Returns an object for interacting with the Anki database."""

    def __init__(self):  # noqa: D107
        self.review_id_file = "anki_submitted_review_entries.json"

    def query_db(self, query: str) -> list:
        """Returns a result set from anki database."""
        conn = sqlite3.connect(ANKI_DB)
        conn.create_collation("unicase", unicase_collation)
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        return query_result

    def get_user_reviews(self, ending_params: str | None = None) -> pd.DataFrame:
        """Returns general data on reviews completed in Anki.

        Note:
        - ending_params is to be used for any extra sql that would be
        valid after the from caluse. i.e (where, limit, ect)
        """
        sql_for_reviews = f"""
            with reviews as (
                select
                    id as review_id
                    , datetime(round(id/1000), 'unixepoch') as review_at_utc
                    , cid as card_id
                    , ease as user_ease_rating
                    , lastivl as last_interval
                    , ivl as new_interval
                    , factor as new_ease_factor
                    , round(time/1000.0,0) as review_time_sec
                    , type as card_review_type
                from revlog

            ), card_mapping as (
                select
                    cards.id as card_id
                    , decks.id as deck_id
                    , decks.name as deck_name
                from cards
                left join decks
                    on decks.id = cards.did

            ), result as (
                select
                    reviews.*
                    , card_mapping.deck_name
                from reviews
                left join card_mapping
                    on reviews.card_id = card_mapping.card_id

            )
            select *
            from result
            {ending_params}
        """

        review_columns = {
            "review_id": int,
            "review_at_utc": "datetime64[ns]",
            "card_id": int,
            "user_ease_rating": int,
            "last_interval": int,
            "new_interval": int,
            "new_ease_factor": int,
            "review_time_sec": int,
            "card_review_type": int,
            "deck_name": str,
        }
        reviews = self.query_db(sql_for_reviews)
        review_df = pd.DataFrame(reviews, columns=review_columns.keys())
        # Convert columns to specified data types
        for col, dtype in review_columns.items():
            review_df[col] = review_df[col].astype(dtype)

        def fix_text(text):
            """Quick function to replace invalid text."""
            cleaned_text = re.sub(r"[\x00-\x1F\x7F-\x9F]", r"/", text or "")
            return cleaned_text

        review_df["deck_name"] = review_df["deck_name"].apply(fix_text)
        return review_df
