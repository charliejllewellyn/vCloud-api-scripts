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
        vcd_type = "application/vnd.vmware.vcloud."+type+"+xml"
        for child in item:
            if child.get("type").lower() == vcd_type.lower():
                if type == "org":
                    org = make_vcd_org_object(child.get("href"), child.get("type"), child.get("name"))
                    array.append(org)
            if child.get("type").lower() == vcd_type.lower():
                if type == "vdc":
                    vcd = make_vcd_vdc_object(child.get("href"), child.get("type"), child.get("name"))
                    array.append(vcd)
            if child.get("type").lower() == vcd_type.lower():
                if type == "vApp":
                    vapp = make_vcd_vapp_object(child.get("href"), child.get("type"), child.get("name"), child.tag)
                    array.append(vapp)
            if child.get("type").lower() == vcd_type.lower():
                if type == "vm":
                    vmRef = make_vcd_vm_object(child.get("href"), child.get("type"), child.get("name"))
                    array.append(vmRef)

        return(array)

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

class vcd_vapp_object(object):
    href = ""
    type = ""
    name = ""
    tag = ""

def make_vcd_vapp_object(href, type, name, tag):
    vcd_vapp = vcd_vapp_object()
    vcd_vapp.href = href
    vcd_vapp.type = type
    vcd_vapp.name = name
    vcd_vapp.tag = tag
    return vcd_vapp

class vcd_vm_object(object):
    href = ""
    type = ""
    name = ""
    IpAddress = ""

def make_vcd_vm_object(href, type, name, IpAddress):
    vcd_vm = vcd_vm_object()
    vcd_vm.href = href
    vcd_vm.type = type
    vcd_vm.name = name
    vcd_vm.IpAddress = IpAddress
    return vcd_vm

def returnVDCs(auth):
    org=queryAPI('https://compute.cloud.eduserv.org.uk/api/org', auth, "Org", "org")
    for o in org:
        #array=list()
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
            print("vApp name: "+vApp.name+" | "+vApp.href+" | "+vApp.tag)
        return(vApps)

def returnVMs(auth):
    vApps=returnvApps(auth)
    for vApp in vApps:
        VMs=queryAPI(vApp.href, auth, "Vm", "vm")
        for VM in VMs:
            print("VM name: "+VM.name)
        return(VMs)

def main():
    auth=login(vcloud_url, username,password, api_version)
    #returnvApps(auth)
    returnVMs(auth)
    #debugAPI('https://compute.cloud.eduserv.org.uk/api/vApp/vapp-0363701e-49ee-4957-ab91-18c2db971f02', auth)
    #debugAPI("https://compute.cloud.eduserv.org.uk/api/vApp/vm-d4d29f63-abb5-49e7-b1fe-ed78098d3e63", auth)
main()





