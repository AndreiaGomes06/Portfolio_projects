from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from datetime import datetime as dt
import os
import pprint
from dotenv import load_dotenv, find_dotenv
# load of the password
load_dotenv(find_dotenv()) 

uri = os.environ.get("MONGODB_PWD")

client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
dbs = client.list_database_names()
production = client.production

printer = pprint.PrettyPrinter()

def create_book_collection():
    # Schema Validation
    book_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [ "title", "authors", "publish_date", "type", "copies" ],
            "properties": {
                "title": {
                "bsonType": "string",
                "description": "'title' must be a string and is required"
                },
                "authors": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "objectId", 
                        "description": "must be and objectId and is required"
                    }
                },
                "publish_date": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                },
                "type": {
                    "enum": ["Fiction", "Non-Fiction"],
                    "description": "can be only one of the enum values and is required",
                },
                "copies": {
                "bsonType": "int",
                "minimum": 0,
                "description": "must be an integer greater than 0 and is required"
                }
            }
        }
        }

    # Exeption to not create a new collection everytime the code runs
    try:
        production.create_collection("book")
    except Exception as e:
        print(e)

    # Modifie the collection so when docs are inserted the schema will be inforced
    production.command("collMod", "book", validator=book_validator)

#create_book_collection()

def create_author_collection():
    author_validator = {
         "$jsonSchema": {
            "bsonType": "object",
            "required": ["first_name", "last_name", "date_of_birth"],
            "properties": {
                "first_name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "last_name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "date_of_birth": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                }
            }
         }
    }

    try:
        production.create_collection("author")
    except Exception as e:
        print(e)

    production.command("collMod", "author", validator=author_validator)

#create_author_collection()
    

def create_data():
    authors = [
        {"first_name": "Margaret",
         "last_name": "Atwood",
         "date_of_birth": dt(1939, 11, 18)},
         {"first_name": "Stephen",
         "last_name": "King",
         "date_of_birth": dt(1947, 9, 18)},
         {"first_name": "J.K.",
         "last_name": "Rowling",
         "date_of_birth": dt(1965, 7, 31)},
         {"first_name": "George R.R.",
         "last_name": "Martin",
         "date_of_birth": dt(1948, 9, 20)},
         {"first_name": "Paulo",
         "last_name": "Coelho",
         "date_of_birth": dt(1947, 8, 24)},
         {"first_name": "Haruki",
         "last_name": "Murakami",
         "date_of_birth": dt(1949, 1, 12)},
         {"first_name": "Dan",
         "last_name": "Brown",
         "date_of_birth": dt(1964, 6, 22)},
         {"first_name": "Agatha",
         "last_name": "Christie",
         "date_of_birth": dt(1890, 9, 15)},
    ]

    author_collection = production.author
    authors = author_collection.insert_many(authors).inserted_ids

    # Reference the authors collection
    books = [
        {"title": "The Handmaid's Tale",
         "authors": [authors[0]],    # References the author id and is inside of a list cause it can have various authors
         "publish_date": dt(1985, 3, 5),
         "type": "Non-Fiction",
         "copies": 5},
         {"title": "A Game of Thrones",
         "authors": [authors[3]],
         "publish_date": dt(1996, 11, 20),
         "type": "Fiction",
         "copies": 400000},
         {"title": "The Da Vinci Code",
         "authors": [authors[6]],
         "publish_date": dt(2003, 7, 23),
         "type": "Non-Fiction",
         "copies": 6000},
         {"title": "The Alchemist",
         "authors": [authors[4]],
         "publish_date": dt(1988, 1, 8),
         "type": "Fiction",
         "copies": 700},
         {"title": "Alias Grace,",
         "authors": [authors[0]],
         "publish_date": dt(1996, 6, 14),
         "type": "Non-Fiction",
         "copies": 462},
         {"title": "Murder on the Orient Express",
         "authors": [authors[7]],
         "publish_date": dt(1934, 12, 7),
         "type": "Fiction",
         "copies": 584},
    ]

    book_collection = production.book
    book_collection.insert_many(books)

#create_data()

# Advanced Queries

# Retrive all the books that contain the letter 'a', uses a regular expression ($regex) to find at least 1 'a'
books_containing_a = production.book.find({"title": {"$regex": "a{1}"}})

printer.pprint(list(books_containing_a))


# Join operation - Agreggate authors and the books they wrote
# "$lookup" performs a left outer join, "localfield" is the field in author to match
# and "foreignField" is the corresponding match in book collection; "as" is the result entry name
pipeline_0 = [
    {
        "$lookup": {
                "from": "book",
                 "localField": "_id",
                 "foreignField": "authors",
                 "as": "books"
                }
    }
]

authors_and_books = production.author.aggregate(pipeline_0)

printer.pprint(list(authors_and_books))


# Count the number of books each author has
pipeline_1 = [
    {
        "$lookup": {
                "from": "book",
                 "localField": "_id",
                 "foreignField": "authors",
                 "as": "books"
                }
    },
    {
        "$addFields": {
            "total_books": {
                "$size": "$books"
                }
            }
    },
    {
        "$project": {
            "first_name": 1, "last_name": 1, "total_books": 1, "_id": 0
            }
    }
]

authors_book_count = production.author.aggregate(pipeline_1)

printer.pprint(list(authors_book_count))


# Find the books with authors who are in between 50 and 150 years old
pipeline_2 = [
    {
        "$lookup": {
                "from": "author",
                 "localField": "authors",
                 "foreignField": "_id",
                 "as": "authors"
                }
    },
    {
        "$set": {
            "authors": {
                "$map": {
                    "input": "$authors",
                            "in": {
                                "age": {
                                    "$dateDiff": {
                                        "startDate": "$$this.date_of_birth",
                                        "endDate": "$$NOW",
                                        "unit": "year"
                                    }
                                },
                                "first_name": "$$this.first_name",
                                "last_name": "$$this.last_name",
                            }
                        }
                    }
                }
    },
    {
        "$match": {
            "$and": [
                {"authors.age": {"$gte": 50}},
                {"authors.age": {"$lte": 150}}
            ]
        }
    },
    {
        "$sort": {
            "authors.age": 1
        }
    }
]

books_with_old_authors = production.book.aggregate(pipeline_2)

printer.pprint(list(books_with_old_authors))


# -------------------------------------------------------------------

# Transform a collection into a dataframe and a numpy array
import pyarrow
from pymongoarrow.api import Schema
from pymongoarrow.monkey import patch_all
import pymongoarrow as pma

# pach_all as the API's features to read as a specific object
patch_all()

author = Schema({"_id": ObjectId, "first_name": pyarrow.string(), "last_name": pyarrow.string(), "date_of_birth": dt})

# Going to transform author collection into a dataframe
df = production.author.find_pandas_all({}, schema=author)
print(df.head())

# Going to transform author collection into a nparray
nparray = production.author.find_numpy_all({}, schema=author)
print(nparray)