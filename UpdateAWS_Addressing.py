# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# UpdateAWS_Addressing.py
# Created on: 2017-07-31 09:49:17.00000
#   This process used to stop and start services to update data and avoid schema lock ; 
# #the new process however doesn't require services to be stopped to update data. 
# However we still kept the old function definition in case we want to switch back(38-96).
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, os.path, 
from arcpy import env
# Import pywin modules that are used to make connection to the folders on AWS. in ArcGIS 10.6, locators have to be stored outside of sde databases
import win32api
import win32net
arcpy.AddMessage("imported win32api and win32net")

print (arcpy.CheckProduct("ArcInfo"))
if arcpy.CheckProduct("ArcInfo") == "Available":
    import arcinfo
elif arcpy.CheckProduct("ArcEditor") == "Available":
    import arceditor
else:
    print("None of the Info or Editor licenses are available")
arcpy.AddMessage(arcpy.ProductInfo())



#Gather inputs for connecting to folder on AWS
userName='Username'
userPassword='Password'
use_dict={}
use_dict['remote']=unicode('\\\\gis.scottcountyiowa.com\\GIS')
use_dict['password']=unicode(userPassword)
use_dict['username']=unicode(userName)
win32net.NetUseAdd(None, 2, use_dict)
'''
# Gather inputs  for connecting to AWS ArcGIS Server  
server ="gis.scottcountyiowa.com" 
port = "6443"
adminUser = "Username" 
adminPass =  "Password" 
stopStart_Stop = "Stop"
stopStart_Start ="Start"
serviceList = "Tools//ScottCountyComposite"

#define stopStartServices
# Import arcpy module
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
    '''Function to stop, start or delete a service.
    Requires Admin user/password, as well as server and port (necessary to construct token if one does not exist).
    stopStart = Stop|Start|Delete
    serviceList = List of services. A service must be in the <name>.<type> notation
    If a token exists, you can pass one in for use.  '''
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
    '''dir_path="\\\\srv-chs-gis04\\E$\\GIS\\Python_Scripts"'''
    env.workspace = os.path.join(dir_path,"AWS")
    arcpy.env.overwriteOutput = True



    # Local variables:
    #address points feature class INTERNAL AND AWS
    SCFeatures_DBO_ADD_Address_SC = "Database Connections\\SCFeatures-srv-chs-gis05.sde\\SCFeatures.DBO.ADD_Address_SC"
    General_Features_SC_DBO_ADD_Address_SC = "Database Connections\\General_Features_SC.sde\\General_Features_SC.DBO.Addressing\\General_Features_SC.DBO.ADD_Address_SC"
    #roads feature class INTERNAL AND AWS
    SCFeatures_DBO_TRANS_Road_SC = "Database Connections\\SCFeatures-srv-chs-gis05.sde\\SCFeatures.DBO.TRANS_Road_SC"
    General_Features_SC_DBO_TRANS_Road_SC = "Database Connections\\General_Features_SC.sde\\General_Features_SC.DBO.TRANS_Road_SC"
    #three locators that are updated on AWS. STAR OF THE SHOW: LOC_Composite_SC
    DBO_LOC_AddressPoint_SC = "\\\\gis.scottcountyiowa.com\\GIS\\AWS_Locators\\LOC_AddressPoint_SC"
    DBO_LOC_Road_SC = "\\\\gis.scottcountyiowa.com\\GIS\\AWS_Locators\\LOC_Road_SC"
    DBO_LOC_Composite_SC = "\\\\gis.scottcountyiowa.com\\GIS\\AWS_Locators\\LOC_Composite_SC"
    
    # Process: Truncate Table
    arcpy.TruncateTable_management(General_Features_SC_DBO_ADD_Address_SC)
    
    arcpy.AddMessage("Truncated the features in address feature on aws")
    # Process: Append
    arcpy.Append_management(SCFeatures_DBO_ADD_Address_SC, General_Features_SC_DBO_ADD_Address_SC, "TEST", "", "")
    
    arcpy.AddMessage("Appended address features on SCfeatures to address feature layer on AWS")
    # Process: Rebuild Address Locator
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_AddressPoint_SC)
    
    arcpy.AddMessage("rebuild address locator on AWS")
    # Process: Truncate Table (2)
    arcpy.TruncateTable_management(General_Features_SC_DBO_TRANS_Road_SC)
        
    arcpy.AddMessage("Truncated the features in road feature on AWS")
    # Process: Append (2)
    arcpy.Append_management(SCFeatures_DBO_TRANS_Road_SC, General_Features_SC_DBO_TRANS_Road_SC, "TEST", "", "")
    
    arcpy.AddMessage("Appended road features on SCfeatures to road feature layer on AWS")
    # Process: Rebuild Address Locator (2)
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_Road_SC)
    
    arcpy.AddMessage("rebuild address locator based on road centerline on AWS")
    # Process: Rebuild Address Locator (3)
    arcpy.RebuildAddressLocator_geocoding(DBO_LOC_Composite_SC)
    
    arcpy.AddMessage("rebuild composite address locator on AWS")
except Exception:
    e = sys.exc_info()[1]
    print(e.args[0])


