"""
This module provides functions for querying the Anki database.
"""

import sqlite3
import re
import pandas as pd

def unicase_collation(s1, s2):
    """
    A utility function that provides collation for handling 
    queries involving tables with non standard text in sqlite3.
    """
    return s1.lower() == s2.lower()

class AnkiDB:
    """
    Returns an object for interacting with the Anki database.
    """

    def __init__(self):
        self.db_path = r"C:\Users\Antho\AppData\Roaming\Anki2\User 1\collection.anki2"

    def query_db(self, query:str):
        """
        Returns a result set from anki database.
        """
        conn = sqlite3.connect(self.db_path)
        conn.create_collation('unicase', unicase_collation)
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        return query_result

    def get_user_reviews(self, ending_parameters:str=None) -> pd.DataFrame:
        """
        Returns data on reviews completed in Anki.
        """
        sql_for_reviews = f'''
            with reviews as (
                select 
                    datetime(round(id/1000), 'unixepoch') as review_at_utc
                    , cid as card_id
                    , ease as user_ease_rating
                    , lastivl as last_interval
                    , ivl as new_interval
                    , factor as new_ease_factor
                    , time as review_time
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
            {ending_parameters}
        '''

        review_columns = {
            'review_at_utc': 'datetime64[ns]',
            'card_id': int,
            'user_ease_rating': int,
            'last_interval': int,
            'new_interval': int,
            'new_ease_factor': int,
            'review_time': int,
            'card_review_type': int,
            'deck_name': str,
        }
        reviews = self.query_db(sql_for_reviews)
        reviews = pd.DataFrame(reviews, columns=review_columns.keys())

        # Convert columns to specified data types
        for col, dtype in review_columns.items():
            reviews[col] = reviews[col].astype(dtype)

        def fix_text(text):
            cleaned_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', r'/', text or '')
            return cleaned_text
        reviews['deck_name'] = reviews['deck_name'].apply(fix_text)
        return reviews

    def create_habitify_entry(self, reviews:pd.DataFrame):
        """
        Returns a entry for habitify
        """

        return

anki = AnkiDB()

result = anki.get_user_reviews()
print(result)

result.to_csv('tests.csv')
