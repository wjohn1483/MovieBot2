#!/bin/bash

# Generate templates
python3 ./template_generator/generate_nlu_data.py # Need to modify the path at the top

# Generate slot table (index to slots)
mv ./codes/generate_slot_tables.py .
python3 generate_slot_tables.py
mv generate_slot_tables.py ./codes/

# Generate values and intent table (index to intent)
python3 ./codes/generate_values_for_jieba.py

# Generate training data and testing data
python3 ./codes/data_generator.py

# Generate word table (vocab to index)
python3 ./codes/generate_word_table.py
