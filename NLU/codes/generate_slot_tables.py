# You need to move this file to working directory to successfully execute
from ontology import OntologyManager
import json

ontologyManager = OntologyManager.OntologyManager()

# Save all slots to one table
all_slots = ontologyManager.get_all_slots()
slot_table = {}
for i, slot in enumerate(all_slots):
    slot_table[i] = all_slots[i]
json.dump(slot_table, open("./data/slots_table.json", 'w'), indent=4)
