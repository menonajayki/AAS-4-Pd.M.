import json
import datetime
import basyx.aas.backend.couchdb
import pyecma376_2
from basyx.aas import model, backend, adapter
from basyx.aas.adapter import json as aas_json
from pathlib import Path
from basyx.aas.adapter import aasx

def create_simple_aas():
    asset_information = model.AssetInformation(
        asset_kind=model.AssetKind.INSTANCE,
        global_asset_id='http://acplt.org/Simple_Asset'
    )

    aas = model.AssetAdministrationShell(
        id_='https://acplt.org/Simple_AAS',
        asset_information=asset_information
    )

    identifier = 'https://acplt.org/Simple_Submodel'
    submodel = model.Submodel(
        id_=identifier
    )

    aas.submodel.add(model.ModelReference.from_referable(submodel))

    semantic_reference = model.ExternalReference(
        (model.Key(
            type_=model.KeyTypes.GLOBAL_REFERENCE,
            value='http://acplt.org/Properties/SimpleProperty'
        ),)
    )

    property_ = model.Property(
        id_short='ExampleProperty',
        value_type=model.datatypes.String,
        value='exampleValue',
        semantic_id=semantic_reference
    )

    file_store = aasx.DictSupplementaryFileContainer()
    with open(Path(__file__).parent / 'TestFile.pdf', 'rb') as f:
        actual_file_name = file_store.add_file("/aasx/suppl/MyExampleFile.pdf", f, "application/pdf")
    submodel.submodel_element.add(
        model.File(id_short="documentationFile",
                   content_type="application/pdf",
                   value=actual_file_name))

    submodel.submodel_element.add(property_)


    # Save file_store as an attribute of the AAS object for later use
    aas.file_store = file_store

    return aas

def serialize_to_json(aas):
    # Serialize AAS to JSON
    aas_json_string = json.dumps(aas, cls=aas_json.AASToJsonEncoder)
    return aas_json_string

def create_object_store(aas):
    # Create ObjectStore and add AAS
    obj_store = model.DictObjectStore()
    obj_store.add(aas)
    return obj_store
print("\nAAS Function.")
# Create a simple AAS
simple_aas = create_simple_aas()

# Serialize AAS to JSON
aas_json_string = serialize_to_json(simple_aas)

# Create ObjectStore and add AAS
object_store = create_object_store(simple_aas)

# Save AAS as .AASX file
aasx_file_path = r"/MyAASXPackage.aasx"
with aasx.AASXWriter(aasx_file_path) as writer:
    # Use a separate file_store for writing
    writer.write_aas(aas_ids=[simple_aas.id], object_store=object_store, file_store=simple_aas.file_store)

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
couchdb_object_store.add(simple_aas)

# Commit changes to CouchDB
simple_aas.commit()

print("\nAAS written to CouchDB.")


# Specify the path to the AASX package file
aasx_file_path = r"/MyAASXPackage.aasx"

# Create new ObjectStore and SupplementaryFileContainer
new_object_store = model.DictObjectStore()
new_file_store = aasx.DictSupplementaryFileContainer()

# Use AASXReader as a context manager to ensure proper file closing
with aasx.AASXReader(aasx_file_path) as reader:
    # Read all contained AAS objects and all referenced auxiliary files
    reader.read_into(object_store=new_object_store, file_store=new_file_store)

    # Get AAS by ID from the ObjectStore
    loaded_aas = new_object_store.get('https://acplt.org/Simple_AAS')

    if loaded_aas:
        # Print loaded AAS
        print("Read MyPackageAASX file:")
        print(f"ID: {loaded_aas.id}")
        print(f"Asset Information: {loaded_aas.asset_information}")

        # Get ModelReference from AAS
        loaded_model_reference = loaded_aas.submodel.pop()

        # Fetch the actual Submodel from the ObjectStore using the ModelReference
        loaded_model_reference = loaded_aas.submodel.pop() if loaded_aas.submodel else None

        if loaded_model_reference:
            # Get the referenced Submodel directly from the ModelReference
            loaded_submodel = new_object_store.get(loaded_model_reference.referable_id)

            if loaded_submodel:
                # Print loaded Submodel
                print("\nLoaded Submodel:")
                print(f"ID: {loaded_submodel.id}")
                print(f"Submodel Elements: {loaded_submodel.submodel_element}")

                # Print loaded Property from Submodel
                loaded_property = loaded_submodel.submodel_element.pop() if loaded_submodel.submodel_element else None
                if loaded_property:
                    print("\nLoaded Property:")
                    print(f"ID: {loaded_property.id_short}")
                    print(f"Value Type: {loaded_property.value_type}")
                    print(f"Value: {loaded_property.value}")
                    print(f"Semantic ID: {loaded_property.semantic_id}")
                else:
                    print("Property not found in the Submodel.")
            else:
                print("Submodel not found in the ObjectStore.")
        else:
            print("ModelReference not found in the AAS.")
