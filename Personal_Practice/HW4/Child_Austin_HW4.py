import arcpy
import csv
import os

def parseTweets(pathToCSV):
    """ Parses each tweet for userID, postedTime, latitude, longitude


        Parameters:
            pathToCSV (string): path (local) to csv file

        Returns:
            tupleList (list): a list of tuples that contain userID, 
                postedTime, latitude & longitude
    """
    tupleList = []
    f = open(pathToCSV, 'r')

    try:
        next(f) 
        rows = csv.reader(f, delimiter=',') 

        # Iterate through each row
        for row in rows:
            # Check to see if there is a lat or long included
            if row[3].strip() == "" or row[4].strip()== "":
                continue #skip the row with empty coordinate

            userID = row[1]
            postedTime = row[2]
            latitude = row[3]
            longitude = row[4]

            tupleList.append((userID, postedTime, latitude, longitude))

    except Exception as error:
        print(error)
    finally:
        if f != None:
            f.close()

    return tupleList

def countTweets(userID, tupleList):
    """ Counts the number of tweets from one user

    Parameters:
        userID (string): the unique user ID
        tupleList (list): a list of tuples that contain userID, 
            postedTime, latitude & longitude

    Returns:
        count (int): the number of posts from a single user
    """
    count = 0
    for tweet in tupleList:
        if tweet[0] == userID:
            count += 1

    return count

def generateShapefile (tupleList, shapefilePath):
    """ Generates a shapefile for all tweets with one attribute: userID

    Parameters:
        tupleList (list): a list of tuples that contain userID, 
            postedTime, latitude & longitude
        shapefilePath (string): the ouput file location

    """
    # Build spatial reference
    sr = arcpy.SpatialReference(4326)

    # Build arcpy feature class
    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(shapefilePath),
        out_name=os.basename.dirname(shapefilePath),
        geometry_type="POINT",
        spatial_reference=sr
    )

    # Add userID as an attribute
    arcpy.AddField_management(shapefilePath, 'userID', 'TEXT')

    # Iterate through and build outfile
    with arcpy.da.InsertCursor(shapefilePath, ['SHAPE@', 'userID']) as cursor:

        # Iterate through each attribute
        for userID, _, lat, lon in tupleList:
            # Find point and add to database
            point = arcpy.Point(float(lon), float(lat))
            pointGeom = arcpy.PointGeometry(point, sr)
            cursor.insertRow((pointGeom, userID))

def printfirst10():
    """Print the first ten lines of the tweets csv"""
    data = parseTweets('/Users/chilaust/Documents/GIS/GisPro/Personal_Practice/HW4/tweetsForOctoberFlood(1).csv')
    for i in range(10):
        print(f'User ID: {data[i][0]} Time: {data[i][1]}, Latitude: {data[i][2]}, Longitude: {data[i][3]}')

# Get the input file as the first tool parameter
input_file = arcpy.GetParametersAsText(0)

# Get the output file as the second tool parameter
output_file = arcpy.GetParametersAsText(1)

# Generate the data from the CSV
data = parseTweets(input_file)

# Output as a shapefile
generateShapefile (data, output_file)








