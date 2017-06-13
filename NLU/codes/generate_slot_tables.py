# You need to move this file to working directory to successfully execute
import sys
import json

with open('./config', 'r') as f:
    path = f.readline().strip().split('=')[1]
    sys.path.append(path)

from ontology import OntologyManager

ontologyManager = OntologyManager.OntologyManager()

# Save all slots to one table
all_slots = ontologyManager.get_all_slots()
slot_table = {}
slot_table[0] = "O"
for i, slot in enumerate(all_slots):
    slot_table[i+1] = all_slots[i]
json.dump(slot_table, open("./data/slots_table.json", 'w'), indent=4)
