# Anki db reader
A simple package for reading from anki database.

# Quickstart

## Installation 🛠️

From PyPI
anki_reader is available on PyPI. To install with `pip`, just run

```
pip install anki_reader
```

##  Setup 🔨

Review the `.env.example` file for the required environment variables

## Usage - Commands/Features

This covers the main use cases for the library.

```python
# create anki object
anki = AnkiDB()

# get user reviews - a premade query (returns df)
reviews = anki.get_user_reviews()
print(reviews)

# get . from database - any query you write (returns df)
cards = anki.query_db("select * from cards limit 5")
print(cards)

```

# Development  🔧
