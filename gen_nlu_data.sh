#!/bin/bash
bash ./setup.sh

# Generate templates
python3 ./template_generator/generate_template.py
python3 ./template_generator/generate_nlu_data.py

# Generate slot table (index to slots)
python3 ./NLU/codes/generate_slot_tables.py

# Generate values and intent table (index to intent)
python3 ./NLU/codes/generate_values_for_jieba.py

# Generate training data and testing data
python3 ./NLU/codes/data_generator.py

# Generate word table (vocab to index)
python3 ./NLU/codes/generate_word_table.py
