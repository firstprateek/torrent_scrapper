import libtorrent as lt
import time
import sys

ses = lt.session()
ses.listen_on(6881, 6891)
info = lt.torrent_info('temp-xx.torrent')
h = ses.add_torrent({'ti': info, 'save_path': './'})
print 'starting', h.name()
counter = 0
while (not h.is_seed() and counter < 10):
    counter += 1
    s = h.status()
    p = h.get_peer_info()
    for peer in p:
      print("Peer ip: {0}, up_speed: {1}, down_speed: {2}".format(peer.ip, peer.up_speed, peer.down_speed))

    print "\n\n"

    sys.stdout.flush()

    time.sleep(3)

print h.name(), 'complete'