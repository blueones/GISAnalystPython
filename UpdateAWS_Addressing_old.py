# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# UpdateAWS_Addressing.py
# Created on: 2017-07-31 09:49:17.00000
# This process used to stop and start services to update data and avoid schema lock ; the new process however doesn't require services to be stopped to update data. 
# However we still kept the old function definition for references(31-85).
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, os.path, 
from arcpy import env

print (arcpy.CheckProduct("ArcInfo"))
if arcpy.CheckProduct("ArcInfo") == "Available":
    import arcinfo
elif arcpy.CheckProduct("ArcEditor") == "Available":
    import arceditor
else:
    print("None of the Info or Editor licenses are available")
print (arcpy.ProductInfo())
# Gather inputs    
server ="my_remote_server" 
port = "port_number"
adminUser = "my_account" 
adminPass =  "my_password" 
stopStart_Stop = "Stop"
stopStart_Start ="Start"
serviceList = "Tools//ScottCountyComposite"

'''
#define stopStartServices

import urllib, urllib2, json

def gentoken(server, port, adminUser, adminPass, expiration=60):
    #Re-usable function to get a token required for Admin changes
    
    query_dict = {'username':   adminUser,
                  'password':   adminPass,
                  'expiration': str(expiration),
                  'client':     'requestip'}
    
    query_string = urllib.urlencode(query_dict)
    url = "https://{}:{}/arcgis/admin/generateToken".format(server, port)
    
    token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())
        
    if "token" not in token:
        arcpy.AddError(token['messages'])
        quit()
    else:
        return token['token']


def stopStartServices(server, port, adminUser, adminPass, stopStart, serviceList, token=None):  
    '''
    ''' Function to stop, start or delete a service.
    Requires Admin user/password, as well as server and port (necessary to construct token if one does not exist).
    stopStart = Stop|Start|Delete
    serviceList = List of services. A service must be in the <name>.<type> notation
    If a token exists, you can pass one in for use.  
    '''
    '''    
    
    # Get and set the token
    if token is None:       
        token = gentoken(server, port, adminUser, adminPass)
    
    # Getting services from tool validation creates a semicolon delimited list that needs to be broken up
    services = serviceList.split(';')
    
    #modify the services(s)    
    for service in services:        
        service = urllib.quote(service.encode('utf8'))
        op_service_url = "https://{}:{}/arcgis/admin/services/{}/{}?token={}&f=json".format(server, port, service, stopStart, token)        
        status = urllib2.urlopen(op_service_url, ' ').read()
        
        if 'success' in status:
            arcpy.AddMessage(str(service) + " === " + str(stopStart))
        else:
            arcpy.AddWarning(status)
    
    return
'''

try:
    # Set environment settings(by using os.path.realpath(), the script can be moved and not break if the relative path stays the same)
    
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    '''dir_path="\\\\srv-chs-efs-02\\county\\GIS\\AWS"'''
    env.workspace = os.path.join(dir_path,"PythonScripts")
    arcpy.env.overwriteOutput = True



    # Local variables:
    SCFeatures_DBO_ADD_Address_SC = "Database Connections\\SCFeatures-srv-chs-gis05.sde\\SCFeatures.DBO.ADD_Address_SC"
    General_Features_SC_DBO_ADD_Address_SC = "Database Connections\\General_Features_SC_AWS.sde\\General_Features_SC.DBO.Addressing\\General_Features_SC.DBO.ADD_Address_SC"
    DBO_LOC_AddressPoint_SC = "Database Connections\\General_Features_SC_AWS.sde\\DBO.LOC_AddressPoint_SC"
    SCFeatures_DBO_TRANS_Road_SC = "Database Connections\\SCFeatures-srv-chs-gis05.sde\\SCFeatures.DBO.TRANS_Road_SC"
    General_Features_SC_DBO_TRANS_Road_SC = "Database Connections\\General_Features_SC_AWS.sde\\General_Features_SC.DBO.Addressing\\General_Features_SC.DBO.TRANS_Road_SC"
    DBO_LOC_Road_SC = "Database Connections\\General_Features_SC_AWS.sde\\DBO.LOC_Road_SC"
    DBO_LOC_Composite_SC = "Database Connections\\General_Features_SC_AWS.sde\\DBO.LOC_Composite_SC"
    
    # Process: Truncate Table
    arcpy.TruncateTable_management(General_Features_SC_DBO_ADD_Address_SC)
    
    print "Truncated the features in address feature on aws"
    # Process: Append
    arcpy.Append_management(SCFeatures_DBO_ADD_Address_SC, General_Features_SC_DBO_ADD_Address_SC, "NO_TEST", "", "")
    
    print "Appended address features on SCfeatures to address feature layer on AWS"
    # Process: Rebuild Address Locator
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_AddressPoint_SC)
    
    print "rebuild address locator on AWS"
    # Process: Truncate Table (2)
    arcpy.TruncateTable_management(General_Features_SC_DBO_TRANS_Road_SC)
        
    print "Truncated the features in road feature on AWS"
    # Process: Append (2)
    arcpy.Append_management(SCFeatures_DBO_TRANS_Road_SC, General_Features_SC_DBO_TRANS_Road_SC "TEST", "", "")
    
    print "Appended road features on SCfeatures to road feature layer on AWS"
    # Process: Rebuild Address Locator (2)
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_Road_SC)
    
    print "rebuild address locator based on road centerline on AWS"
    # Process: Rebuild Address Locator (3)
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_Composite_SC)
    
    print "rebuild composite address locator on AWS"
except Exception:
    e = sys.exc_info()[1]
    print(e.args[0])


