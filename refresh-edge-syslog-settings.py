__author__ = 'CLlewellyn'

import requests
import sys
import re
import os
import time
import threading
import xml.etree.ElementTree as xml
import getpass
import argparse

vCloudUrl = "https://api.vcd.portal.skyscapecloud.com"

user = raw_input('Please enter you API username: ')
if os.name == "nt":
    pwd = getpass.win_getpass()
else:
    pwd = getpass.getpass(prompt='Please enter your password:')

headers = { 'Accept': 'application/*+xml;version=5.5'}
exitFlag = 0

def vcdLogin(vCloudUrl, username, password):
    r = requests.post(vCloudUrl + "/api/sessions", auth=(user, pwd), headers=headers)
    token = r.headers.get('x-vcloud-authorization')
    if not token:
        print("Couldn't login please try again.")
        sys.exit(1)
    return token

def setHeaders(token, newHeaders=None):
    headers = {'Accept': 'application/*+xml;version=5.5', 'x-vcloud-authorization': token}
    if newHeaders:
        headers.update(newHeaders)
    return headers

def queryVcd(href, token, method="GET", data=None, headers=headers):
    if method == "GET":
        try:
            r = requests.get(href, headers=headers)
        except Exception:
            print("Failed to query " + href)
    if method == "POST":
        try:
            r = requests.post(href, headers=headers, data=data)
        except Exception:
            print("Failed to query " + href)
    if method == "PUT":
        try:
            r = requests.put(href, headers=headers, data=data)
        except Exception:
            print("Failed to query " + href)
    if method == "DELETE":
        try:
            r = requests.delete(href, headers=headers)
        except Exception:
            print("Failed to query " + href)
    return r

def vcdLogout(vCloudUrl, token):
    queryVcd(vCloudUrl + "/api/sessions", token, method="DELETE", headers=setHeaders(token))

def queryXml(xmlString, path=None, attrib=None, attribVal=None ):
    if re.match("^http://.*", vCloudUrl):
        xmlString = re.sub("https://", "http://", xmlString)
    if not path:
        path = '.'
    if attrib:
        path = path + "[@" + attrib + "='" + attribVal + "']"
    namespaces={'ovf' : "http://schemas.dmtf.org/ovf/envelope/1", "vcloud" : "http://www.vmware.com/vcloud/v1.5" ,
                "rasd" : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData"}
    tree = xml.fromstring(xmlString)
    xmlElements = []
    for i in tree.iterfind(path, namespaces=namespaces):
        xmlElements.append(i)
    return xmlElements

# Login to vCloud
token = vcdLogin(vCloudUrl, user, pwd)
# Get edge Gateway Refs for org
xmlString = queryVcd(vCloudUrl + "/api/query?type=edgeGateway", token, headers=setHeaders(token)).text
# Update edge refs to target syslog refresh enpoint
edgeHref = queryXml(xmlString, 'vcloud:EdgeGatewayRecord')[0].get("href")
edgeSyslogSet = edgeHref + "/action/syncSyslogServerSettings"
# POST to endpoint to refresh syslog settings
print(queryVcd(edgeSyslogSet, token, method="POST", headers=setHeaders(token)).text)
# Logout of vCloud
vcdLogout(vCloudUrl, token)
