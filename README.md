torrent-ip-checker
==================

Script that runs a fake tracker that only reports back the IP of the connecting client. Using this tracker, BitTorrent users can verify their IPs by opening a special test torrent. This is useful if you've taken steps to hide your IP address, and wish to check that your setup is working correctly.

The script supports both the UDP tracker protocol (see [BEP 15](http://www.bittorrent.org/beps/bep_0015.html)), and the TCP tracker protocol (see the [Tracker HTTP/HTTPS Protocol](https://wiki.theory.org/BitTorrentSpecification#Tracker_HTTP.2FHTTPS_Protocol)).
