import json
from basyx.aas import model, backend, adapter
from basyx.aas.adapter import json as aas_json
from pathlib import Path
from basyx.aas.adapter import aasx

class OTAUpdateAAS:
    def __init__(self):
        # Define AAS properties
        self.current_version_property = model.Property(
            id_short='CurrentVersion',
            value_type=model.datatypes.String,
            value='1.0',
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value='http://acplt.org/Properties/CurrentVersion'
                ),)
            )
        )

        self.available_updates_property = model.Property(
            id_short='AvailableUpdates',
            value_type=model.datatypes.Integer,
            value=0,
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value='http://acplt.org/Properties/AvailableUpdates'
                ),)
            )
        )

        # Create AAS
        self.aas = model.AssetAdministrationShell(
            id_='https://acplt.org/OTAUpdateAAS',
            asset_information=model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id='http://acplt.org/OTAUpdateAsset'
            )
        )

        # Add properties to submodel
        submodel = model.Submodel(id_='https://acplt.org/OTAUpdateSubmodel')
        submodel.submodel_element.add(self.current_version_property)
        submodel.submodel_element.add(self.available_updates_property)
        self.aas.submodel.add(model.ModelReference.from_referable(submodel))

        # Save file_store as an attribute of the AAS object for later use
        self.aas.file_store = aasx.DictSupplementaryFileContainer()

    def initiate_update(self):
        # Implement the InitiateUpdate function
        print("Initiating update...")

    def rollback(self):
        # Implement the Rollback function
        print("Rolling back to the previous version...")

    def print_values(self):
        # Print values of AAS
        print("AAS:")
        print(f"ID: {self.aas.id}")
        print(f"Asset Information: {self.aas.asset_information}")

        # Print values of Submodel
        submodel = self.aas.submodel.pop() if self.aas.submodel else None
        if submodel:
            print("\nSubmodel:")
            print(f"ID: {submodel.id}")

            print(f"Submodel Elements: {submodel.submodel_element}")

            # Print values of Property
            property_ = submodel.submodel_element.pop() if submodel.submodel_element else None
            if property_:
                print("\nProperty:")
                print(f"ID: {property_.id_short}")
                print(f"Value Type: {property_.value_type}")
                print(f"Value: {property_.value}")
                print(f"Semantic ID: {property_.semantic_id}")
            else:
                print("Property not found in the Submodel.")
        else:
            print("Submodel not found in the AAS.")

# Create OTAUpdateAAS instance
ota_update_aas = OTAUpdateAAS()

# Print values
ota_update_aas.print_values()

# Serialize AAS to JSON
aas_json_string = ota_update_aas.serialize_to_json()

# Create ObjectStore and add AAS
object_store = ota_update_aas.create_object_store()

# Save AAS as .AASX file
aasx_file_path = r"OTAUpdateAAS.aasx"
with aasx.AASXWriter(aasx_file_path) as writer:
    # Use a separate file_store for writing
    writer.write_aas(aas_ids=[ota_update_aas.aas.id], object_store=object_store, file_store=ota_update_aas.aas.file_store)

# Rest of the code remains the same for writing to CouchDB and reading from AASX file
