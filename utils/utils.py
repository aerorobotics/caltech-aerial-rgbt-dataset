import numpy as np


def read_class_index_color_hex_csv(file):
    index_color_name_mapping = {}
    with open(file, 'r') as f:
        for line in f.readlines():
            row = line.strip().split(',')
            idx = int(row[0])
            name = row[1]
            rgb = row[2]
            index_color_name_mapping[idx] = [name, rgb]
    return index_color_name_mapping
