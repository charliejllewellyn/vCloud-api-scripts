__author__ = 'cl'

import urllib.request, base64
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as etree

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

def queryAPI(url, auth, element, type):
    print("Running against vCloud type: " + type)
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
        #item=tree.findall('.//{http://www.vmware.com/vcloud/v1.5}'+type+'[@name=\'sa.eduserv.org.uk\']')
        array=list()
        item = tree.findall('.//{http://www.vmware.com/vcloud/v1.5}'+element)
        type = "application/vnd.vmware.vcloud."+type+"+xml"
        for child in item:

            if child.get("type").lower() == type.lower():
                vcd = make_vcd(child.get("href"), child.get("type"), child.get("name"))
                array.append(vcd)
        return(array)

class vcd_object(object):
    href = ""
    type = ""
    name = ""

def make_vcd(href, type, name):
    vdc = vcd_object()
    vdc.href = href
    vdc.type = type
    vdc.name = name
    return vdc

def returnVDCs(auth):
    org=queryAPI('https://compute.cloud.eduserv.org.uk/api/org', auth, "Org", "org")
    for o in org:
        array=list()
        for o in org:
            vdc = queryAPI(o.href, auth, "Link", "vdc")
            for v in vdc:
                print("Virtual datacentre name: "+v.name)
        return(vdc)

def returnvApps(auth):
    VDCs=returnVDCs(auth)
    for vdc in VDCs:
        vApps=queryAPI(vdc.href, auth, "ResourceEntity", "vApp")
        for vApp in vApps:
            print("vApp name: "+vApp.name)
        return(vApp)

def main():
    auth=login('https://compute.cloud.eduserv.org.uk/api/sessions', 'charles.llewellyn@eduserv.org.uk@sa.eduserv.org.uk','r3m0t3!0g0n', '5.1')
    returnvApps(auth)

main()





