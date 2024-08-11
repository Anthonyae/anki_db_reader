"""This is a testing module for anki."""

# add .src to the path
import sys

import pandas as pd
import pytest

sys.path.append("src")
from anki_reader import AnkiDB


def test_call_anki_class():
    """Checks to see if anki object exists."""
    obj = AnkiDB()
    assert obj


def test_query_anki_db():
    """Checks to see that the the anki class can query the database."""
    anki = AnkiDB()
    result_set = anki.query_db("select 1 as test")
    assert result_set


def test_query_exception_handling():
    """Confirms that running invalid SQL code returns an error from the AnkiDB class."""
    anki = AnkiDB()
    # raise an exception if the query is invalid
    with pytest.raises(Exception) as exc_info:
        anki.query_db("select 1 as not_working_sql")

    # Now you can check the exception if needed
    assert str(exc_info.value) != "", "Exception should contain an error message"
    print("Exception captured:", exc_info.value)


def test_reviews_dataframe():
    """Checks to seee a dataframe and its post processed column is handled correctly."""
    anki = AnkiDB()
    result_df = anki.get_user_reviews(ending_params="limit 5")
    assert isinstance(result_df, pd.DataFrame)
    assert "deck_name" in result_df.columns
