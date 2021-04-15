# Trackerfraese

This terribly hacked together script queries rtorrent via xmlrpc. It then:
 * goes through its torrents
 * checks each tracker for resolvability and connectability
 * enables or disables the tracker in rtorrent accordingly

DISCLAIMER: This is a pre-alpha hackjob I threw together out of pure annoyance with this bug: https://github.com/rakshasa/rtorrent/issues/999
