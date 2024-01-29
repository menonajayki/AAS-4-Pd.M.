import requests
import numpy as np
import matplotlib.pyplot as plt

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

# Perform Coulomb counting to estimate the state of charge (SoC)
# Assume a constant time interval between data points (for example, 1 second)
time_interval = 1  # in seconds
total_charge = np.sum(data_matrix_current) * time_interval  # Coulombs
battery_capacity_mAh = 5000
capacity = battery_capacity_mAh / 1000
state_of_charge = total_charge / capacity  # Adjust 'capacity' based on battery characteristics

# Visualize the data
time_points = np.arange(len(data_matrix_voltage)) * time_interval

# Plot Voltage
plt.subplot(3, 1, 1)
plt.plot(time_points, data_matrix_voltage, label='Voltage', color='blue')
plt.xlabel('Time (seconds)')
plt.ylabel('Voltage (V)')
plt.legend()

# Plot Current
plt.subplot(3, 1, 2)
plt.plot(time_points, data_matrix_current, label='Current', color='green')
plt.xlabel('Time (seconds)')
plt.ylabel('Current (A)')
plt.legend()

# Ensure SoC has the same length as time_points
state_of_charge = np.resize(state_of_charge, len(time_points))

# Plot State of Charge
plt.subplot(3, 1, 3)
plt.plot(time_points, state_of_charge * 100, label='State of Charge', color='red')
plt.xlabel('Time (seconds)')
plt.ylabel('State of Charge (%)')
plt.legend()

plt.tight_layout()
plt.show()
