import json
import requests
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import quote

# Connect to CouchDB
couchdb_user = "kiajaymenon"
couchdb_password = "ARENA2036"
couchdb_database = "sample_database"
couchdb_url = f'http://{couchdb_user}:{couchdb_password}@127.0.0.1:5984/'
encoded_document_id = "https%3A%2F%2Facplt.org%2FSimple_Submodel"

print(encoded_document_id)


# Make a request to CouchDB
response = requests.get(f'{couchdb_url}/{couchdb_database}/{encoded_document_id}')

if response.status_code == 200:
    couchdb_data = response.json()['data']
else:
    print(f"Error retrieving document from CouchDB. Status code: {response.status_code}")
    print(response.text)  # Print the response content for additional information
    exit()

# Step 2: Parse the matrix data
data_matrix_str = None
for submodel_element in couchdb_data['submodelElements']:
    if submodel_element['idShort'] == 'DataMatrix':
        data_matrix_str = submodel_element['value']
        break

if data_matrix_str is None:
    print("DataMatrix not found in the CouchDB document.")
    exit()

data_matrix = np.array([float(value) for value in data_matrix_str.split(',')])

# Step 3: Detect anomalies (values above 5)
threshold = 5
anomalies = data_matrix[data_matrix > threshold]

# Step 4: Visualize anomalies
plt.plot(data_matrix, label='Sensor Data')
plt.scatter(np.where(data_matrix > threshold), anomalies, color='red', label='Anomalies (above 5)')
plt.axhline(y=threshold, color='orange', linestyle='--', label='Threshold (5)')
plt.xlabel('Index')
plt.ylabel('Sensor Data Value')
plt.legend()
plt.title('Sensor Data and Anomalies')
plt.show()
