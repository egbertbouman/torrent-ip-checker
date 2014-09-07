torrent-ip-checker
==================

Script that runs a fake tracker, and only reports back the IP of the connecting client. Using this tracker, BitTorrent users can verify their IPs by opening a special test torrent. This is useful if you've taken steps to hide your IP address, and wish to check that your setup is working correctly.

For now the script only supports the UDP tracker protocol (see [BEP 15](http://www.bittorrent.org/beps/bep_0015.html)), but I plan to add support for TCP trackers in the future.
