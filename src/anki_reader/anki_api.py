"""This module provides functions for querying the Anki database."""

import os
import re
import sqlite3

import pandas as pd


def windows_to_wsl_path(path_str: str) -> str:
    """Convert a Windows path to a WSL path.

    Convert the drive letter to lowercase and prepend /mnt/ to the path.
    """
    is_running_in_wsl = (
        os.path.exists("/proc/sys/kernel/osrelease")
        and "microsoft" in open("/proc/sys/kernel/osrelease").read().lower()
    )
    if is_running_in_wsl:
        drive, rest_of_path = path_str.split(":\\", 1)
        rest_of_path = rest_of_path.replace("\\", "/")
        linux_path = f"/mnt/{drive.lower()}/{rest_of_path}"
        path_str = linux_path
    else:
        path_str = path_str
    return path_str


def load_env_vars() -> str:
    """Load environment variables from .env file."""
    ANKI_DB = os.getenv("ANKI_DB", "")
    # Determine if the path is a windows path and convert it to a linux path
    ANKI_DB = windows_to_wsl_path(ANKI_DB)
    return ANKI_DB


def unicase_collation(s1, s2) -> bool:
    """A utility function that provides collation for handling queries involving tables with non standard text in sqlite3.

    Returns: wether the two strings are equal or not.
    """
    return s1.lower() == s2.lower()


class AnkiDB:
    """Returns an object for interacting with the Anki database."""

    def __init__(self):  # noqa: D107
        self.ANKI_DATABASE_PATH = load_env_vars()

    def query_db(self, query: str) -> list:
        """Returns a result set from anki database."""
        conn = sqlite3.connect(self.ANKI_DATABASE_PATH)
        conn.create_collation("unicase", unicase_collation)
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        return query_result

    def get_user_reviews(self, ending_params: str | None = None) -> pd.DataFrame:
        """Returns general data on reviews completed in Anki.

        Note:
            - ending_params is to be used for any extra sql that would be valid after
            the from caluse. i.e (where, limit, ect)

        Examples:
            - "where review_at_utc >= date('{YYY-MM-DD}') and review_at_utc <= date('{YYYY-MM-DD}') limit 5"
            - "where review_at_utc >= date('2025-01-01') limit 5"
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
        review_df = pd.DataFrame(reviews, columns=review_columns.keys())  # type: ignore
        # Convert columns to specified data types
        for col, dtype in review_columns.items():
            review_df[col] = review_df[col].astype(dtype)

        def fix_text(text):
            """Quick function to replace invalid text."""
            cleaned_text = re.sub(r"[\x00-\x1F\x7F-\x9F]", r"/", text or "")
            return cleaned_text

        review_df["deck_name"] = review_df["deck_name"].apply(fix_text)
        return review_df
