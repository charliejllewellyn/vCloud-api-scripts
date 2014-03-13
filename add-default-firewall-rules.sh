#!/bin/bash

Authurl='https://xxxxx.xxx/'

echo "Please enter you username"
read username
echo "Please enter your password"
read -s password
echo "Please enter the org name e.g. demo.eduserv.org.uk"
read org
#org='education.gov.uk'
echo "Please enter the vdc name e.g. demo.eduserv.org.uk_SDC_A01"
read vdc
#vdc='education.gov.uk_SDC_A03'
echo "Please enter customer type (std|dfe)"
read cust
if [ "$cust" == "" ]; then
        echo You must enter a customer type of std of dfe. Please try again...
elif [ "$cust" == "dfe" ]; then
        file='rules-dfe.txt'
elif [ "$cust" == "std" ]; then
        file='rules-dfe.txt'
fi

username=${username}@System

# Get auth token
curl -i -k -H "Accept:application/*+xml;version=5.1" -u ${username}:$password -X POST ${Authurl}api/sessions &>sessionID.txt
xAuth=`grep x-vcloud-authorization sessionID.txt | awk '{print $2}'`
grep 'HTTP/1.1 200 OK' sessionID.txt &>/dev/null
if [ $? != 0 ]; then
        echo "Authentication to vCloud failed please try again..."
fi
echo Logged in

echo Getting Org...
# Get org ref
curl -i -k -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}" -X GET ${Authurl}api/admin &>Ref.txt
OrgRef=`grep $org Ref.txt | grep href | awk '{print $NF}' | sed 's/href="//g' | sed 's/"\/>//g'`

#echo Getting Org Network...
# Get VDC Ref
curl -i -k -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}" -X GET $OrgRef &>Ref.txt
vdcRef=`grep 'vnd.vmware.admin.vdc+xml' Ref.txt | grep "$vdc" | awk '{print $NF}' | sed 's/href="//g' | sed 's/"\/>//g'`
# | awk '{print $NF}' | sed 's/href="//g' | sed 's/"\/>//g'`

# Get admin gateway ref
curl -i -k -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}" -X GET ${vdcRef} &>Ref.txt
Network=`grep 'vnd.vmware.admin.edgeGateway+xml' Ref.txt | awk '{print $NF}' | sed 's/href="//g' | sed 's/"\/>//g'`

# Get admin version of gateway
curl -i -k -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}" -H "Content-Type:application/vnd.vmware.vcloud.query.records+xml" -X GET ${Network} &>Ref.txt
Gateway=`grep 'EdgeGatewayRecord' Ref.txt | awk '{print $9}' | sed 's/href="//g' | sed 's/"//g'`

# Query Gateway for xml
curl -i -k -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}" -H "Content-Type:application/vnd.vmware.vcloud.query.records+xml" -X GET ${Gateway} > Gateway.xml
EditGateway=`grep 'configureServices' Gateway.xml | awk '{print $NF}' | sed 's/href="//g' | sed 's/"\/>//g'`

############### Create Gateway xml ##############
echo -e "<EdgeGatewayServiceConfiguration xmlns=\"http://www.vmware.com/vcloud/v1.5\">\n<FirewallService>" > FW.txt
while read line
do
        name=`echo $line | awk -F, '{print $1}'`
        policy=`echo $line | awk -F, '{print $2}'`
        protocol=`echo $line | awk -F, '{print $3}'`
        if [ "$protocol" == "icmp" ] ; then
                IcmpSubType='<IcmpSubType>any</IcmpSubType>'
        fi
        if [ "$protocol" == "tcp" ]; then
                protocol='<Tcp>true</Tcp>'
        elif [ "$protocol" == "udp" ]; then
                protocol='<Udp>true</Udp>'
        elif [ "$protocol" == "icmp" ]; then
                protocol='<Icmp>true</Icmp>'
        elif [ "$protocol" == "both" ]; then
                protocol='<Tcp>true</Tcp>\n\t\t\t<Udp>true</Udp>'
        elif [ "$protocol" == "any" ]; then
                protocol='<Any>true</Any>'
        fi
        srcPortRange=`echo $line | awk -F, '{print $4}'`
        srcPort=`echo $line | awk -F, '{print $4}'`
        if [ "$srcPortRange" == "any" ] || [ "*-*" ]; then
                srcPort="-1"
        fi
        dstPortRange=`echo $line | awk -F, '{print $5}'`
        dstPort=`echo $line | awk -F, '{print $5}'`
        if [ "$dstPortRange" == "any" ] || [ "*-*" ]; then
                dstPort="-1"
        fi
        src=`echo $line | awk -F, '{print $6}'`
        dst=`echo $line | awk -F, '{print $7}'`
echo -e "
                <FirewallRule>
                    <IsEnabled>true</IsEnabled>
                    <MatchOnTranslate>false</MatchOnTranslate>
                    <Description>$name</Description>
                    <Policy>$policy</Policy>
                    <Protocols>
                        $protocol
                    </Protocols>
                    $IcmpSubType
                    <Port>$dstPort</Port>
                    <DestinationPortRange>$dstPortRange</DestinationPortRange>
                    <DestinationIp>$dst</DestinationIp>
                    <SourcePort>$srcPort</SourcePort>
                    <SourcePortRange>$srcPortRange</SourcePortRange>
                    <SourceIp>$src</SourceIp>
                    <EnableLogging>true</EnableLogging>
                </FirewallRule>" >> FW.txt
IcmpSubType=""
done < $file
echo -e "</FirewallService>\n</EdgeGatewayServiceConfiguration>" >> FW.txt

# Update Gateway
curl -i -k  -H "Accept:application/*+xml;version=5.1" -H "x-vcloud-authorization: ${xAuth}x" -H "Content-Type:application/vnd.vmware.admin.edgeGatewayServiceConfiguration+xml" -X POST ${EditGateway} -d @FW.txt
