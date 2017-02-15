#------------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:        Create Buffers from Point
#
# Purpose:     For demonstration on how to build a custom ArcGIS Desktop tool using the ArcPy library.
#              Presented at the February 2017 Harrisburg GIS Meetup.  The tool combines multiple geoprocessing
#              tools into a single tool that accepts user parameters.
#
# Description: The tool takes a latitude and longitude value and creates a WGS 1984 point.  The point is then re-projected
#              into the Pennsylvania State Plane South (ft) projection.  A multi-ring buffer analysis is performed on the re-projected point.
#
# Author:      Patrick McKinney, Cumberland County GIS, PAMAGIC
#
# Created:     2/13/2017
#
# Copyright:   (c) Cumberland County 2017
#
# Github:      https://github.com/pmacMaps
#
# Disclaimer: CUMBERLAND COUNTY ASSUMES NO LIABILITY ARISING FROM USE OF THESE MAPS OR DATA. THE MAPS AND DATA ARE PROVIDED WITHOUT
#             WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#             FITNESS FOR A PARTICULAR PURPOSE.
#             Furthermore, Cumberland County assumes no liability for any errors, omissions, or inaccuracies in the information provided regardless
#             of the cause of such, or for any decision made, action taken, or action not taken by the user in reliance upon any maps or data provided
#             herein. The user assumes the risk that the information may not be accurate.
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

# Import system modules
import arcpy
import os, sys, time, datetime, traceback, string

# User-defined variables from tool's dialog window
# See http://pro.arcgis.com/en/pro-app/arcpy/functions/getparameterastext.htm
# Latitude of site - input
lat = arcpy.GetParameterAsText(0)
# Longitude of site - input
lon = arcpy.GetParameterAsText(1)
# Projected point layer - output
spcPoint = arcpy.GetParameterAsText(2)
# Buffer distance - input
buffDist = arcpy.GetParameterAsText(3)
# Buffer units - input
buffUnits = arcpy.GetParameterAsText(4)
# Buffer layer - output
pointBuffer = arcpy.GetParameterAsText(5)

# Component functions for tool.
# Function to write a message to ArcGIS dialog window
def addMessage(message):
    """ Adds a message to the ArcGIS dialog window"""
    # get current time
    currentTime = datetime.datetime.now()
    # format time for message - 01-01-2017 10:00:00
    formattedTime = currentTime.strftime("%m-%d-%Y %H:%M:%S")
    # add message to tool's dialog window
    # See http://pro.arcgis.com/en/pro-app/arcpy/functions/addmessage.htm
    arcpy.AddMessage('{} : {} \n \n'.format(formattedTime, message))
# end function AddMessage()

# Create geometry point from latitude/longitude and convert to PA State Plane South (ft) coordinate system
# You could add user parameters so that this function can convert from WGS 1984 to a user defined coordinate system
def createSPCPoint(lat, lon, outLayer):
    """Converts WGS 1984 latitude/longitude coordinates to PA State Plane South (feet)"""
    try:
        # Spatial reference variables
        # See http://pro.arcgis.com/en/pro-app/arcpy/classes/spatialreference.htm
        # WGS 1984 spatial reference
        srWGS84 = arcpy.SpatialReference(4326)
        # PA State Plane South (feet) NAD 1983 spatial reference
        srSPC = arcpy.SpatialReference(2272)

        # create point from user entered latitude and longitude
        # See http://pro.arcgis.com/en/pro-app/arcpy/classes/point.htm
        point = arcpy.Point(lon, lat)

        # create geometry point (WGS 1984)
        # See http://pro.arcgis.com/en/pro-app/arcpy/classes/pointgeometry.htm
        geometryPoint = arcpy.PointGeometry(point, srWGS84)

        # Add message
        addMessage('Created WGS 1984 point for latitude: {} and longitude {}.'.format(lat, lon))

        # Convert WGS 1984 layer to a NAD 1983 PA State Plane South layer
        # See https://pro.arcgis.com/en/pro-app/tool-reference/data-management/project.htm
        # If projected coordinate system is user defined, you may need to add a user input for transform method
        # assign geoprocessing tool to a variable to access messages from tool
        result = arcpy.Project_management(geometryPoint, outLayer, srSPC, "NAD_1983_To_WGS_1984_1", preserve_shape = "PRESERVE_SHAPE")

        # capture geoprocessing results message
        # delay writing results until geoprocessing tool gets the completed code
        while result.status < 4:
            time.sleep(0.2)
        # See http://pro.arcgis.com/en/pro-app/arcpy/functions/getmessages.htm
        resultValue = result.getMessages()
        # add results message to ArcGIS dialog window
        arcpy.AddMessage(resultValue + '\n \n')

        # Add message
        addMessage('Reprojected point from WGS 1984 to PA State Plane South (feet).')

    # if an error occured, write this to dialog window
    except Exception:
        # error message
        e = sys.exc_info()[1]
        # See http://pro.arcgis.com/en/pro-app/arcpy/functions/adderror.htm
        arcpy.AddError(e.args[0] + '\n \n')
        # Add generic error message about tool
        arcpy.AddError('There was an error running this tool \n \n')
# end createSPCPoint()

def createBuffers(point, outLayer, distances, units):
    """ Create a multi-ring buffer from an point layer"""
    try:
        # Create a multi-ring buffer of point
        # See http://pro.arcgis.com/en/pro-app/tool-reference/analysis/multiple-ring-buffer.htm
        # assign geoprocessing tool to a variable to access messages from tool
        result = arcpy.MultipleRingBuffer_analysis(point, outLayer, distances, units)

        # capture geoprocessing results message
        # delay writing results until geoprocessing tool gets the completed code
        while result.status < 4:
            time.sleep(0.2)
        # See http://pro.arcgis.com/en/pro-app/arcpy/functions/getmessages.htm
        resultValue = result.getMessages()
        # add results message to ArcGIS dialog window
        arcpy.AddMessage(resultValue + '\n \n')

        # Add Message
        addMessage('Created buffer(s) around location latitude: {}; longitude: {}.'.format(lat, lon))
    # if an error occured, write this to dialog window
    except Exception:
        # error message
        e = sys.exc_info()[1]
        # See http://pro.arcgis.com/en/pro-app/arcpy/functions/adderror.htm
        arcpy.AddError(e.args[0] + '\n \n')
        # Add generic error message about tool
        arcpy.AddError('There was an error running this tool \n \n')
# end createBuffer()

# Run tools with user inputs
addMessage('Converting WGS 1984 point to PA State Plane South (feet) point.')

# Run createSPCPoint() function
createSPCPoint(lat, lon, spcPoint)

# Run createBuffer() function
createBuffers(spcPoint, pointBuffer, buffDist, buffUnits)

# Add message
addMessage('Create Buffer from Point tool has completed running.')