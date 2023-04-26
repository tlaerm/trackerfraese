#!/usr/bin/python3
from xmlrpc.client import ServerProxy, Error
import argparse
import dnsq
import re
import os
import socket
import struct

server = ServerProxy("http://localhost:8000")
processedTrackers = dict()

def check_udp_tracker(host,port):
    clisocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clisocket.settimeout(1.0)
    connection_id=0x41727101980
    transaction_id = 12345
    action = 0x0
    buffer = struct.pack("!q", connection_id)  # first 8 bytes is connection id
    buffer += struct.pack("!i", action)  # next 4 bytes is action
    buffer += struct.pack("!i", transaction_id)  # next 4 bytes is transaction id
    clisocket.sendto(buffer, (host, port))
    try:
        res = clisocket.recv(1024)
        return res
    except socket.timeout:
        return False

def check_http_port(host, port):
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    a_socket.settimeout(1.0)
    try:
        if a_socket.connect_ex((host,port)) == 0:
            return True
    except Exception:
        return False
    finally:
        a_socket.close()

def process_torrent(torrent):
    trackerindex = 0
    print("------------------------------------")
    print(server.d.name(torrent))
    for tracker in server.t.multicall(torrent, "", "t.url="):

        tracker = str(tracker.pop())

        if tracker not in processedTrackers:
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
            print("Tracker with index %d protocol %s host %s port %s" % (trackerindex, protocol, host, port), end=" - ")
            print("Not in cache, checking", end=" - ")

            if len(dnsq.query_dns(host, 'a')) > 0 :
                ip = dnsq.query_dns(host, 'a').pop()
                print("resolvable, ip is "+ip, end=" - ")

                if protocol == 'udp':

                    res = check_udp_tracker(ip,int(port))
                    if res:
                        status = True
                        print("port alive", end=" - ")
                    else:
                        status = False
                        print("port dead", end=" - ")
                else:
                    res = check_http_port(ip,port)
                    if res:
                        status = True
                        print("port alive", end=" - ")
                    else:
                        status = False
                        print("port dead", end=" - ")
            else:
                # print("Tracker with index %d protocol %s host %s port %s" % (trackerindex, protocol, host, port), end=" - ")

                print("not resolvable", end=" - ")
                status = False
        else:
            print(tracker+" cached", end=" - ")
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

def parse_args():
    parser = argparse.ArgumentParser(description='DESCRIPTION')
    parser.add_argument('torrents', default=[], nargs='*')
    return parser.parse_args()

def get_from_api():
    return server.download_list()

def main():
    args = parse_args()

    for torrent_id in (args.torrents or get_from_api()):
        process_torrent(torrent_id)


if __name__ == '__main__':
    main()
