import couchdb

# Connect to CouchDB
couchdb_user = "kiajaymenon"
couchdb_password = "ARENA2036"
couchdb_database = "sample_database"
couchdb_url = f'http://{couchdb_user}:{couchdb_password}@127.0.0.1:5984/'

# Connect to the CouchDB server
server = couchdb.Server(couchdb_url)

# Access the desired database
db = server[couchdb_database]

# Delete all documents in the database
for doc_id in db:
    doc = db[doc_id]
    db.delete(doc)

print("All documents deleted successfully.")
