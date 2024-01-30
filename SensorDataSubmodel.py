import csv
import pandas as pd
from io import StringIO
import datetime
from pathlib import Path
import pyecma376_2
from basyx.aas.adapter import aasx
from basyx.aas import model, backend
import basyx.aas.backend.couchdb
import numpy as np

# read the sensor data file
file_path = 'dataset.csv'
df = pd.read_csv(file_path)


# Read current and voltage
voltage_matrix = df['Voltage(V)'].to_numpy()
current_matrix = df['Current(A)'].to_numpy()
print(voltage_matrix)
print(current_matrix)

# Converting voltage matrix to a string
voltage_data = voltage_matrix
csv_string = StringIO()
csv_writer = csv.writer(csv_string)
csv_writer.writerow(voltage_data)
csv_string.seek(0)
voltage_data_value = csv_string.read().strip()


# Converting current matrix to a string
current_data = current_matrix
csv_string = StringIO()
csv_writer = csv.writer(csv_string)
csv_writer.writerow(current_data)
csv_string.seek(0)
current_data_value = csv_string.read().strip()

submodelVoltage = model.Submodel(
    id_='https://acplt.org/Voltage_Submodel',
    submodel_element=[
        model.Property(
            id_short='Voltage',
            value_type=model.datatypes.String,
            value=voltage_data_value,
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value='http://example.org/Properties/Voltage'
                ),)
            )
        )
    ]
)

submodelCurrent = model.Submodel(
    id_='https://acplt.org/Current_Submodel',
    submodel_element=[
        model.Property(
            id_short='Current',
            value_type=model.datatypes.String,
            value=current_data_value,
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value='http://example.org/Properties/Current'
                ),)
            )
        )
    ]
)

ota_aas = model.AssetAdministrationShell(
    id_='https://acplt.org/Sensor_AAS',
    asset_information=model.AssetInformation(
        asset_kind=model.AssetKind.INSTANCE,
        global_asset_id='http://acplt.org/Simple_Asset'

    ),
    submodel=[model.ModelReference.from_referable(submodelVoltage), model.ModelReference.from_referable(submodelCurrent)]

)



unrelated_submodel = model.Submodel(
    id_='https://acplt.org/Unrelated_Submodel'
)

object_store = model.DictObjectStore([submodelVoltage, submodelCurrent, ota_aas, unrelated_submodel])

file_store = aasx.DictSupplementaryFileContainer()

with open(Path(__file__).parent / 'TestFile.pdf', 'rb') as f:
    actual_file_name = file_store.add_file("/aasx/suppl/MyExampleFile.pdf", f, "application/pdf")


submodelVoltage.submodel_element.add(
    model.File(id_short="documentationFile",
               content_type="application/pdf",
               value=actual_file_name))

with aasx.AASXWriter("MyAASXPackage.aasx") as writer:
    writer.write_aas(aas_ids=[ota_aas.id], object_store=object_store, file_store=file_store)
    objects_to_be_written = model.DictObjectStore([unrelated_submodel])
    writer.write_all_aas_objects(part_name="/aasx/my_aas_part.xml",
                                 objects=objects_to_be_written,
                                 file_store=file_store)
    meta_data = pyecma376_2.OPCCoreProperties()
    meta_data.creator = "I am the vehicle owner"
    meta_data.created = datetime.datetime.now()
    writer.write_core_properties(meta_data)
    print("Generated AASX file:", Path("MyAASXPackage.aasx").resolve())

new_object_store = model.DictObjectStore()
new_file_store = aasx.DictSupplementaryFileContainer()

with aasx.AASXReader("MyAASXPackage.aasx") as reader:
    print("\nReading the AASX File.................................")
    # Read all contained AAS objects and all referenced auxiliary files
    reader.read_into(object_store=new_object_store, file_store=new_file_store)

    # Get AAS and Submodel from the object store
    loaded_aas = new_object_store.get('https://acplt.org/Simple_AAS')
    loaded_submodel1 = new_object_store.get('https://acplt.org/Voltage_Submodel')
    loaded_submodel2 = new_object_store.get('https://acplt.org/Current_Submodel')

    if loaded_aas and loaded_submodel1 and loaded_submodel2:
        # Print AAS information
        print("\nLoaded AAS:")
        print(f"ID: {loaded_aas.id}")
        print(f"Asset Information: {loaded_aas.asset_information}")

        # Print Submodel information
        print("\nLoaded Voltage Submodel:")
        print(f"ID: {loaded_submodel1.id}")
        print(f"Submodel Elements: {loaded_submodel1.submodel_element}")

        # Extract and print matrix data for Submodel 1 (Voltage)
        voltage_matrix_str = None
        for submodel_element in loaded_submodel1.submodel_element:
            if submodel_element.id_short == 'Voltage':
                voltage_matrix_str = submodel_element.value
                break
        if voltage_matrix_str is not None:
            # Convert voltage_matrix_str to a NumPy array
            voltage_matrix = np.array([float(value) for value in voltage_matrix_str.split(',')])
            print("Voltage Data:")
            print(voltage_matrix)
        else:
            print("DataMatrix not found in the loaded Voltage Submodel.")



        # Print Submodel information
        print("\nLoaded Current Submodel:")
        print(f"ID: {loaded_submodel2.id}")
        print(f"Submodel Elements: {loaded_submodel2.submodel_element}")

        # Extract and print matrix data for Submodel 2 (Current)
        current_matrix_str = None
        for submodel_element in loaded_submodel2.submodel_element:
            if submodel_element.id_short == 'Current':
                current_matrix_str = submodel_element.value
                break

        if current_matrix_str is not None:
            # Convert current_matrix_str to a NumPy array
            current_matrix = np.array([float(value) for value in current_matrix_str.split(',')])
            print("Current Data:")
            print(current_matrix)
        else:
            print("DataMatrix not found in the loaded Current Submodel.")


    else:
        print("AAS or Submodel not found in the object store.")

    # Connect to CouchDB
    couchdb_user = "kiajaymenon"
    couchdb_password = "ARENA2036"
    couchdb_database = "sample_database"
    couchdb_url = f'http://{couchdb_user}:{couchdb_password}@127.0.0.1:5984/'

    # Register credentials for CouchDB
    backend.couchdb.register_credentials(couchdb_url, couchdb_user, couchdb_password)

    # Create CouchDBObjectStore
    couchdb_object_store = backend.couchdb.CouchDBObjectStore(couchdb_url, couchdb_database)

    # Add AAS to CouchDBObjectStore
    couchdb_object_store.add(ota_aas)
    couchdb_object_store.add(submodelVoltage)
    couchdb_object_store.add(submodelCurrent)
    # Commit changes to CouchDB
    ota_aas.commit()

    print("\nAAS data is written to CouchDB. AAS and Submodels Created. Start the Predicive Maintenance")
