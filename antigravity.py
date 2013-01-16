from utils import *
import re


ip_regex = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

''' os agnostic section '''

#read file
def fileContents(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

#network - ip to host (DNS)
def getHostName(ip):
    from socket import gethostbyaddr
    return gethostbyaddr(ip)[0]

'''
not all the commands will return - eg. output from nbtstat can't be read
'''
def osCommand(cmd, shellOn=True, combineOutErr = True):
    from subprocess import Popen, PIPE
    import os
    output = Popen(cmd, shell=shellOn, stdout=PIPE, stderr=PIPE, env=os.environ.copy()).communicate()
    
    if combineOutErr:
        return output[0]+output[1]
    return output

#windows-only

'''
does a network login - don't use this to brute force - may lock out
host = ip address or host name
name = domain\username
returns 'The command completed successfully.' if successful
'''
def testCreds_ipc(host, name, passwd = '', removeShare = True):
    retval = osCommand(r'net use \\%s\ipc$ /u:"%s" "%s"' % (host,name,passwd))
    if removeShare:
        osCommand('net use \\%s\ipc$ /delete')
    return retval


username_regex = r'\b(\w+\\\w+)\b'
mac_regex = r'((\w\w:){5}\w\w)'
#returns list of tuples: ip,hostname,mac
#ip can be of the form
#uses nbtscan -> http://www.unixwiz.net/tools/
def netbios(inputForNbtscan, debug=False):
    output = osCommand("nbtscan -f %s" % inputForNbtscan)
    if debug:
        print output
    outputlines = output.split('\r\n')
    ipNameList = []
    for line in outputlines:
        for m in re.finditer(ip_regex, line):
            if m.start() == 0:
                ip = line[0:m.end()]
                m2 = re.search(username_regex, line)
                name = line[m.end():]
                if m2 != None:
                    name = m2.group(0)
        regexMatch = re.search(mac_regex, line)
        mac = ''
        if regexMatch != None:
            mac = regexMatch.group(0)
            print mac
            ipNameList.append((ip,name,mac))
    return ipNameList
