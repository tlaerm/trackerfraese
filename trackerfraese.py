#!/usr/bin/python3
import pprint
from xmlrpc.client import ServerProxy, Error
import dnsq
import re
import os
processedTrackers = dict()

server = ServerProxy("http://localhost:8000")

for torrent in server.download_list():
    trackerindex = 0
    print("------------------------------------")
    print(server.d.name(torrent))
    for tracker in server.t.multicall(torrent, "", "t.url="):
    
        tracker = str(tracker.pop())
        pprint.pprint(tracker)
        
        if tracker not in processedTrackers:
            print("Not in cache, checking ...")
            rgx1 = r"\/\/([a-zAZ0-9\.\-]*)[\:0-9]*"
            rgx2 = r"\:([0-9]{2,5})"
            rgx3 = r"^([a-z]*)\:"
            result = re.search(rgx1, tracker)
            result2 = re.search(rgx2, tracker)
            result3 = re.search(rgx3, tracker)
            protocol = result3.group(1)
            if protocol == 'dht':
              print("skipping dht")
              continue
            
            host = result.group(1)
             
            try:
                port = result2.group(1)
            except:
                if protocol == "http":
                    port = 80
                elif protocol == "https":
                    port = 443
                    
            if len(dnsq.query_dns(host, 'a')) > 0 :
                pprint.pprint("resolvable")
                ip = dnsq.query_dns(host, 'a').pop()
                print("Tracker with index %d protocol %s host %s ip %s port %s" % (trackerindex, protocol, host, ip, port))
                
                if protocol == 'udp':
                
                    res = os.system("nc -w 3 -vnzu "+ip+" "+str(port)+" > /dev/null 2>&1")
                    if res == 0:
                        status = True
                        print("port alive")
                    else:
                        status = False
                        print("port dead")
                elif protocol == 'http':

                    res = os.system("nc -w 3 -vnz "+ip+" "+str(port)+" > /dev/null 2>&1")
                    if res == 0:
                        status = True
                        print("port alive")
                    else:
                        status = False
                        print("port dead")        
                elif protocol == 'https':

                    res = os.system("nc -w 3 -vnz "+ip+" "+str(port)+" > /dev/null 2>&1")
                    if res == 0:
                        status = True
                        print("port alive")
                    else:
                        status = False
                        print("port dead")      
                
            else:
                pprint.pprint("not resolvable")
                status = False
        else:
            print("result from cache")
            status = processedTrackers[tracker]

        if status:
            print("Enabling tracker")
            server.t.enable(torrent+":t"+str(trackerindex))
        else:
            print("Disabling tracker")
            server.t.disable(torrent+":t"+str(trackerindex))
        trackerindex += 1
        
        if tracker not in processedTrackers:
            processedTrackers[tracker] = status

    print("------------------------------------")
