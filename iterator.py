__author__ = 'cl'

import urllib.request, base64
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as etree

username='charles.llewellyn@eduserv.org.uk@sa.eduserv.org.uk'
password=input('Please enter your password:')
vcloud_url='https://compute.cloud.eduserv.org.uk/api/sessions'
api_version='5.1'

def login( url, username, password, version):
    request = urllib.request.Request(url)
    base64string = base64.b64encode(str(username+":"+password).encode('ascii'))
    request.add_header("Authorization", "Basic %s" % base64string.decode("utf-8"))
    request.add_header("Accept", "application/*+xml;version=" + version)
    request.get_method = lambda: 'POST'
    try:
        result = urllib.request.urlopen(request)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
        exit()
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
        exit()
    else:
        res=(result.getheaders())
        auth=''.join(res[5]).replace("x-vcloud-authorization", "")
        return(auth)

def debugAPI(url, auth):
    print("Printing XML for: "+url)
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/*+xml;version=5.1")
    request.add_header("x-vcloud-authorization", auth)
    request.get_method = lambda: 'GET'
    try:
        response = urllib.request.urlopen(request)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
        exit()
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
        exit()
    else:
        XMLresponse=response.read().decode("utf-8")
        print(XMLresponse)

def queryAPI(url, auth):
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/*+xml;version=5.1")
    request.add_header("x-vcloud-authorization", auth)
    request.get_method = lambda: 'GET'
    try:
        response = urllib.request.urlopen(request)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
        exit()
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
        exit()
    else:
        XMLresponse=response.read().decode("utf-8")
        #print(XMLresponse)
        tree = etree.ElementTree(etree.fromstring(XMLresponse))
        list_vcd_objects=list()
        for elt in tree.iter():
            vcd_item = make_vcd_item_object(elt)
            list_vcd_objects.append(vcd_item)
        return(list_vcd_objects)
        #item=tree.findall('.//{http://www.vmware.com/vcloud/v1.5}'+type+'[@name=\'sa.eduserv.org.uk\']')

def returnOrgs(auth):
    items=queryAPI('https://compute.cloud.eduserv.org.uk/api/org', auth)
    list_vcloud_orgs=list()
    for item in items:
        if item.tag.tag == '{http://www.vmware.com/vcloud/v1.5}Org':
            org = make_vcd_org_object(item.tag.get("href"), item.tag.get("type"), item.tag.get("name"))
            list_vcloud_orgs.append(org)
            print(org.name)
    return(list_vcloud_orgs)

def returnVDCs(auth):
    items=returnOrgs(auth)
    list_vcloud_vdcs=list()
    for item in items:
        if item.tag.tag == '{http://www.vmware.com/vcloud/v1.5}Org':
            vdc = make_vcd_vdc_object(item.href, item.type, item.name)
            list_vcloud_vdcs.append(vdc)
            print(vdc.name)
    return(list_vcloud_vdcs)

class vcd_item_object(object):
    tag = ""

def make_vcd_item_object(tag):
    vcd_item = vcd_item_object()
    vcd_item.tag = tag
    return vcd_item

class vcd_org_object(object):
    href = ""
    type = ""
    name = ""

def make_vcd_org_object(href, type, name):
    vcd_org = vcd_org_object()
    vcd_org.href = href
    vcd_org.type = type
    vcd_org.name = name
    return vcd_org

class vcd_vdc_object(object):
    href = ""
    type = ""
    name = ""

def make_vcd_vdc_object(href, type, name):
    vcd_vdc = vcd_vdc_object()
    vcd_vdc.href = href
    vcd_vdc.type = type
    vcd_vdc.name = name
    return vcd_vdc

def main():
    auth=login(vcloud_url, username,password, api_version)
    returnOrgs(auth)
main()