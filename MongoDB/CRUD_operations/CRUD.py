from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import os
import pprint
from dotenv import load_dotenv, find_dotenv
# load of the password
load_dotenv(find_dotenv()) 

password = os.environ.get("MONGODB_PWD")

uri = f"mongodb+srv://pg45463:{password}@cluster0.nw3alsv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
dbs = client.list_database_names()
print(dbs)

test_db = client.test
collections = test_db.list_collection_names()
print(collections)

# Insert one document at time in the collection
def insert_test_doc():
    collection = test_db.test

    test_document = {
        "name": "Tim",
        "type": "Test"
    }

    # Give us the _id of the document that was inserted
    inserted_id = collection.insert_one(test_document).inserted_id 
    print(inserted_id)

#insert_test_doc()

# Creating a new Database called production
production = client.production

# Creating a collection on the new Database
person_collection = production.person_collection

# Insert various documents at once in the collection
def create_documents():
    first_names = ["Tim", "Rose", "Jose", "Brad", "Allen", "Sonia", "Sarah", "Rita"]
    last_names = ["Smith", "Ruscica", "Carter", "Pit", "Parks", "Geral", "Gomez", "Ora"]
    ages = [25, 45, 51, 29, 35, 12, 33, 74]

    docs = []

    for first_name, last_name, age in zip(first_names, last_names, ages):
        doc = {
           "first_name": first_name,
            "last_name": last_name,
            "age": age
        }
        docs.append(doc)
    
    person_collection.insert_many(docs)

#create_documents()
    
printer = pprint.PrettyPrinter()

# Quering the documents

def find_all_people():
    people = person_collection.find()
    #print(list(people))

    for person in people:
        printer.pprint(person)

#find_all_people()
        
def find_rita():
    rita = person_collection.find_one({"first_name": "Rita", "last_name": "Ora"})
    printer.pprint(rita)

#find_rita()

def count_all_people():
    count = person_collection.count_documents(filter={})
    print(f"Number of people: {count}")

#count_all_people()

def get_person_by_id(person_id):

    _id = ObjectId(person_id)
    person = person_collection.find_one({"_id": _id})
    printer.pprint(person)

#get_person_by_id("65e7ac06fa297eac01e2d4d9")

def get_age_range(min_age, max_age):
    query ={"$and": [
            {"age": {"$gte": min_age}},
            {"age": {"$lte": max_age}}
        ]}
    
    age_range = person_collection.find(query).sort("age")

    for range in age_range:
        printer.pprint(range)

#get_age_range(25, 45)
        
def project_columns():
    columns = {"_id": 0, "first_name": 1, "age": 1}
    people = person_collection.find({}, columns)

    for person in people:
        printer.pprint(person)

#project_columns()
        
# Updating the documents
    
def update_person_by_id(person_id):
    _id = ObjectId(person_id)

    all_update = {
        "$set": {"new_field": True},
        "$inc": {"age": 1},
        # Renames the field not the value
        "$rename": {"first_name": "first", "last_name": "last"}
    }

    person_collection.update_one({"_id": _id}, all_update)

#update_person_by_id("65e7ac06fa297eac01e2d4d8")
#get_person_by_id("65e7ac06fa297eac01e2d4d8")
    
def delete_fiel_by_by_id(person_id):
    _id = ObjectId(person_id)
    # We need to set a empty string for the field we want to remove
    person_collection.update_one({"_id": _id}, {"$unset": {"new_field": ""}})
    
#delete_fiel_by_by_id("65e7ac06fa297eac01e2d4d8")
#get_person_by_id("65e7ac06fa297eac01e2d4d8")
    
# The way to update the majority of the field of a document but keep the same id
def replace_one(person_id):
    _id = ObjectId(person_id)

    new_doc = {
        "first_name": "new first name",
        "last_name": "new last name",
        "age": 5
    }

    person_collection.replace_one({"_id": _id}, new_doc)

#replace_one("65e7ac06fa297eac01e2d4d8")
#get_person_by_id("65e7ac06fa297eac01e2d4d8")
    
# Deleting documents
    
def delete_doc_by_id(person_id):
    _id = ObjectId(person_id)

    person_collection.delete_one({"_id": _id})

#delete_doc_by_id("65e7ac06fa297eac01e2d4d8")
#get_person_by_id("65e7ac06fa297eac01e2d4d8")
    
def delete_all_documents():
    person_collection.delete_many({})

# ------------------------------------------------ 

# Relationships
    
address = {
    "_id": "265e7ac06fa297eac01e2d4d8",
    "street": "Moon Street",
    "number": 268,
    "city": "San Francisco",
    "country": "United States of America",
    "zip": "25684"
}

def add_address_embed(person_id, address):
    _id = ObjectId(person_id)
    # Created an array so it can store more than 1 address
    person_collection.update_one({"_id": _id}, {"$addToSet": {"adresses": address}})
    

add_address_embed("65e7ac06fa297eac01e2d4da", address)
get_person_by_id("65e7ac06fa297eac01e2d4da")
    
# To store in a separate collection and create a relation 
def add_address_relationship(person_id, address):

    # To add the owner id to the address
    address = address.copy()
    address["owner_id"] = person_id

    address_collection = production.address
    address_collection.insert_one(address)

#add_address_relationship("65e7ac06fa297eac01e2d4d9", address)
