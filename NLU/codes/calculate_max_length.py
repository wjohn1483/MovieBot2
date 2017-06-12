f = open("./data/training_data.txt", 'r')

max_len = 0
for line in f:
    line = line.rstrip().split()
    if len(line) > max_len: max_len = len(line)

print(max_len)

