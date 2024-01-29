import requests
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Connect to CouchDB
couchdb_user = "kiajaymenon"
couchdb_password = "ARENA2036"
couchdb_database = "sample_database"
couchdb_url = f'http://{couchdb_user}:{couchdb_password}@127.0.0.1:5984/'
encoded_document_id_voltage = "https%3A%2F%2Facplt.org%2FVoltage_Submodel"
encoded_document_id_current = "https%3A%2F%2Facplt.org%2FCurrent_Submodel"

# Make requests to CouchDB for Voltage and Current data
response_voltage = requests.get(f'{couchdb_url}/{couchdb_database}/{encoded_document_id_voltage}')
response_current = requests.get(f'{couchdb_url}/{couchdb_database}/{encoded_document_id_current}')

if response_voltage.status_code == 200 and response_current.status_code == 200:
    couchdb_data_voltage = response_voltage.json()['data']
    couchdb_data_current = response_current.json()['data']
else:
    print(f"Error retrieving documents from CouchDB. Status codes: {response_voltage.status_code}, {response_current.status_code}")
    print(response_voltage.text)  # Print the response content for additional information
    print(response_current.text)
    exit()

# Parse Voltage matrix data
data_matrix_voltage_str = None
for submodel_element in couchdb_data_voltage['submodelElements']:
    if submodel_element['idShort'] == 'Voltage':
        data_matrix_voltage_str = submodel_element['value']
        break

if data_matrix_voltage_str is None:
    print("Submodel for Voltage not found in the CouchDB document.")
    exit()

data_matrix_voltage = np.array([float(value) for value in data_matrix_voltage_str.split(',')])

# Parse Current matrix data
data_matrix_current_str = None
for submodel_element in couchdb_data_current['submodelElements']:
    if submodel_element['idShort'] == 'Current':
        data_matrix_current_str = submodel_element['value']
        break

if data_matrix_current_str is None:
    print("Submodel for Current not found in the CouchDB document.")
    exit()

data_matrix_current = np.array([float(value) for value in data_matrix_current_str.split(',')])

# Calculate Power (simple multiplication for illustration)
power_matrix = data_matrix_voltage * data_matrix_current

# Print the intermediate calculations
print("Voltage Matrix:")
print(data_matrix_voltage)
print("\nCurrent Matrix:")
print(data_matrix_current)
print("\nPower Matrix:")
print(power_matrix)

# Step 3: Detect anomalies (values above 5)
threshold = 4

# Combine Voltage and Current matrices for Isolation Forest
combined_matrix = np.column_stack((data_matrix_voltage, data_matrix_current, power_matrix))

# Fit Isolation Forest model
model = IsolationForest(contamination=0.1)  # Adjust the contamination parameter as needed
model.fit(combined_matrix)

# Predict anomalies
anomalies = model.predict(combined_matrix)

# Print the anomalies
print("\nAnomalies:")
print(anomalies)

# Step 4: Visualize anomalies
plt.plot(power_matrix, label='Power Data')
plt.scatter(np.where(anomalies == -1), power_matrix[anomalies == -1], color='red', label='Anomalies')
plt.axhline(y=threshold, color='orange', linestyle='--', label='Threshold (4W)')
plt.xlabel('Time Units')
plt.ylabel('Power')
plt.legend()
plt.title('Power Data and Anomalies')
plt.show()
