import csv
import os
import numpy as np
import arcpy
from math import radians, sin, cos, atan2, sqrt

def Parse_Data(pathToCSV):

    tupleList = []
    with open(pathToCSV, 'r', encoding='utf-8-sig', newline='') as f:

        try:
            rows = csv.reader(f, delimiter=',') 
            header = next(rows)

            # Iterate through each row
            for row in rows:
                # Check to see if it has all the items
                if len(row) < 18:
                    continue

                # Check to see if there is a lat or long included
                if row[15].strip() == "" or row[16].strip()== "":
                    continue 

                eventID = row[0]
                damage = float(row[5].strip())
                begin_lat = float(row[14].strip())
                begin_lon = float(row[15].strip())
                end_lat = float(row[16].strip())
                end_lon = float(row[17].strip())

                tupleList.append((eventID, damage, begin_lat, begin_lon, end_lat, end_lon))

        except Exception as error:
            print(error)

        finally:
            if f != None:
                f.close()

    return tupleList

def Flood_Damage(pathToCSV):
    data = np.genfromtxt(pathToCSV, delimiter=',', skip_header=1)
    return np.sum(data[:, 5])

def Flood_Damage_2(data):
    sum = 0
    for event in data:
        sum += float(event[1])
    
    return sum

def generateShapefile(tupleList, shapefilePath):
    sr = arcpy.SpatialReference(4326)

    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(shapefilePath),
        out_name=os.path.basename(shapefilePath),
        geometry_type='POINT',
        spatial_reference=sr
    )

    arcpy.AddField_management(shapefilePath, 'eventID', 'TEXT')

    with arcpy.da.InsertCursor(shapefilePath, ['SHAPE@', 'eventID']) as cursor:

        # Iterate through each attribute
        for eventID, _, begin_lat, begin_lon, _, _ in tupleList:
            # Find point and add to database
            begin_point = arcpy.Point(float(begin_lon), float(begin_lat))
            beginpointGeom = arcpy.PointGeometry(begin_point, sr)
            cursor.insertRow((beginpointGeom,  eventID, ))


def distance_traveled(data):
    R = 6373.0

    big_damage_distances = []
    distances = []
    for event in data:
        begin_lat = radians(event[2])
        begin_lon = radians(event[3])
        end_lat = radians(event[4])
        end_lon = radians(event[5])

        dif_lat = end_lat - begin_lat
        dif_lon = end_lon - begin_lon

        a = sin(dif_lat / 2)**2 + cos(begin_lat) * cos(end_lat) * sin(dif_lon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        distance = R * c
        distances.append(distance)

        if event[1] > 100000:
            big_damage_distances.append(distance)

    average_distance = np.mean(distances)
    big_flood_average_distance = np.mean(big_damage_distances)

    return distances, big_damage_distances, average_distance, big_flood_average_distance


# Get the input file as the first tool parameter
input_file = arcpy.GetParameterAsText(0)

output_folder = os.path.dirname(input_file)
base = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(output_folder, base + ".shp")

# Generate the data from the CSV
data = Parse_Data(input_file)

# Output as a shapefile
generateShapefile(data, output_file)



if __name__ == "__main__":
    print('QUESTION 1')
    data = Parse_Data('Flash_Flooding_201504.csv')
    print(f'Total Damage: {Flood_Damage_2(data)}')
    print()

    print('QUESTION 2 \n--see shapefile and attatched images')
    print()

    print('QUESTION 3')
    distances, big_damage_distances, average, big_flood_average_distance = distance_traveled(data)

    print(f'Total average distance: {average}')

    for i, flood in enumerate(distances):
        if i < 10:
            print(f'Flood {i + 1}: {flood}')
        else:
            break
    
    print()
    print('QUESTION 4')
    print(f'Big damage average distance: {big_flood_average_distance}')
    for i, flood in enumerate(big_damage_distances):
        print(f'Flood {i + 1}: {flood}')

    
