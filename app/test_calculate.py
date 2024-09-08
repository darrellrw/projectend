import os
import csv
import configparser

def test_calculate(file_path):
    data = []

    config = configparser.ConfigParser()
    config.read(os.path.join(file_path, "scan_config.ini"))

    with open(os.path.join(file_path, "data_coordinates.csv"), 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            data.append(row[1:])
    
    y = [int(row[1]) for row in data]
    lowest_y = min(y)
    highest_y = max(y)

    x1 = [int(row[0]) for row in data if int(row[1]) >= 0 and int(row[1]) <= 75]
    lowest_x1 = min(x1)
    highest_x1 = max(x1)

    x2 = [int(row[0]) for row in data if int(row[1]) >= 80 and int(row[1]) <= 200]
    lowest_x2 = min(x2)
    highest_x2 = max(x2)

    z1 = [int(row[2]) for row in data if int(row[1]) >= 0 and int(row[1]) <= 75]
    lowest_z1 = min(z1)
    highest_z1 = max(z1)

    z2 = [int(row[2]) for row in data if int(row[1]) >= 80 and int(row[1]) <= 200]
    lowest_z2 = min(z2)
    highest_z2 = max(z2)

    pcm = config.get("Configure", "PCM")

    lenght_y = (highest_y - lowest_y) * float(pcm)
    print(f"Lowest Y: {lowest_y} | Highest Y: {highest_y} | Length Y: {lenght_y} cm")

    lenght_x1 = (highest_x1 - lowest_x1) * float(pcm)
    print(f"Lowest X1: {lowest_x1} | Highest X1: {highest_x1} | Length X1: {lenght_x1} cm")

    lenght_x2 = (highest_x2 - lowest_x2) * float(pcm)
    print(f"Lowest X2: {lowest_x2} | Highest X2: {highest_x2} | Length X2: {lenght_x2} cm")

    lenght_z1 = (highest_z1 - lowest_z1) * float(pcm)
    print(f"Lowest Z1: {lowest_z1} | Highest Z1: {highest_z1} | Length Z1: {lenght_z1} cm")

    lenght_z2 = (highest_z2 - lowest_z2) * float(pcm)
    print(f"Lowest Z2: {lowest_z2} | Highest Z2: {highest_z2} | Length Z2: {lenght_z2} cm")

test_calculate("/home/darrell/Documents/projectend/data/2024-09-08_23-42-34")