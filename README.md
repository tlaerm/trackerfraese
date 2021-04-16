# Trackerfraese

This terribly hacked together script queries rtorrent via xmlrpc. It then:
 * goes through its torrents
 * checks each tracker for resolvability and connectability
 * enables or disables the tracker in rtorrent accordingly

Why: Rtorrent bogs down if it can't reach trackers. If you have a lot of older public torrents with dead trackers it can become unusable. Manually disabling them is theoretically possible but would be very tedious. See this bug for more information: https://github.com/rakshasa/rtorrent/issues/999 

DISCLAIMER: This is a pre-alpha hackjob I threw together out of pure annoyance with this bug.

ToDo:
 * document code
 * add instructions
 * separate configuration
 * test if it works with rtorrent socket

As this works for me as it is, I would only do further work if it helps others use it. Please open an issue, if you want any of these things.
