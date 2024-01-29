import datetime
from pathlib import Path
import pyecma376_2
from basyx.aas import model
from basyx.aas.adapter import aasx

submodel = model.Submodel(
    id_='https://acplt.org/Simple_Submodel'
)
aas = model.AssetAdministrationShell(
    id_='https://acplt.org/Simple_AAS',
    asset_information=model.AssetInformation(
        asset_kind=model.AssetKind.INSTANCE,
        global_asset_id='http://acplt.org/Simple_Asset'
    ),
    submodel={model.ModelReference.from_referable(submodel)}
)

unrelated_submodel = model.Submodel(
    id_='https://acplt.org/Unrelated_Submodel'
)

object_store = model.DictObjectStore([submodel, aas, unrelated_submodel])

file_store = aasx.DictSupplementaryFileContainer()

with open(Path(__file__).parent / 'TestFile.pdf', 'rb') as f:
    actual_file_name = file_store.add_file("/aasx/suppl/MyExampleFile.pdf", f, "application/pdf")

submodel.submodel_element.add(
    model.File(id_short="documentationFile",
               content_type="application/pdf",
               value=actual_file_name))

with aasx.AASXWriter("MyAASXPackage.aasx") as writer:
    writer.write_aas(aas_ids=[aas.id], object_store=object_store, file_store=file_store)
    objects_to_be_written = model.DictObjectStore([unrelated_submodel])
    writer.write_all_aas_objects(part_name="/aasx/my_aas_part.xml",
                                 objects=objects_to_be_written,
                                 file_store=file_store)
    meta_data = pyecma376_2.OPCCoreProperties()
    meta_data.creator = "Chair of Process Control Engineering"
    meta_data.created = datetime.datetime.now()
    writer.write_core_properties(meta_data)
    print("Generated AASX file:", Path("MyAASXPackage.aasx").resolve())

new_object_store = model.DictObjectStore()
new_file_store = aasx.DictSupplementaryFileContainer()

with aasx.AASXReader("MyAASXPackage.aasx") as reader:
    # Read all contained AAS objects and all referenced auxiliary files
    reader.read_into(object_store=new_object_store, file_store=new_file_store)

    # Get AAS and Submodel from the object store
    loaded_aas = new_object_store.get('https://acplt.org/Simple_AAS')
    loaded_submodel = new_object_store.get('https://acplt.org/Simple_Submodel')

    if loaded_aas and loaded_submodel:
        # Print AAS information
        print("Loaded AAS:")
        print(f"ID: {loaded_aas.id}")
        print(f"Asset Information: {loaded_aas.asset_information}")

        # Print Submodel information
        print("\nLoaded Submodel:")
        print(f"ID: {loaded_submodel.id}")
        print(f"Submodel Elements: {loaded_submodel.submodel_element}")

    else:
        print("AAS or Submodel not found in the object store.")