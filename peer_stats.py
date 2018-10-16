import libtorrent as lt
import tempfile
import shutil
import sys
from time import sleep

TORRENT_CREATE_TIMEOUT = 60
TORRENT_DONWLOAD_TIMEOUT = 120

def magnet2torrent(magnet):
  tempdir = tempfile.mkdtemp()
  ses = lt.session()

  def clean_up_before_abort(abort_message):
    print(abort_message)
    ses.pause()
    print("Cleanup dir " + tempdir)
    shutil.rmtree(tempdir)

  params = {
      'save_path': tempdir,
      'storage_mode': lt.storage_mode_t(2),
      'paused': False,
      'auto_managed': True,
      'duplicate_is_error': True
  }
  handle = lt.add_magnet_uri(ses, magnet, params)
  handle.set_upload_limit(0) #DO NOT UPLOAD ANYTHING

  #parse_magnet_uri()

  try:
    print("Downloading Metadata (this may take a while)")
    
    time_spent_converting = 0
    while (not handle.has_metadata()):
      if time_spent_converting >= TORRENT_CREATE_TIMEOUT:
        clean_up_before_abort("Failed to convert magent link -- aborting")
        return -1
      sleep(1)
      time_spent_converting += 1

    
    torinfo = handle.get_torrent_info()
    print("torinfo")
    print(torinfo)
    # ses.pause()
    print("Done")
    print("Starting to download torrent ...")
    #get_torrent_info
    return

    counter = 0
    while (not handle.is_seed() and counter < TORRENT_DONWLOAD_TIMEOUT):
      print("counter: {0}".format(counter))
      counter += 1
      # status = handle.status()
      peer_info = handle.get_peer_info()
      print("peer_info: {0}".format(peer_info))

      for peer in peer_info:
        print("Peer ip: {0}, up_speed: {1}, down_speed: {2}".format(peer.ip, peer.up_speed, peer.down_speed))

      sleep(5)
  except KeyboardInterrupt:
    clean_up_before_abort('Keyboard KeyboardInterrupt Triggered')
    return

  print("Done info gathered ...")
  ses.pause()
  ses.remove_torrent(handle)
  shutil.rmtree(tempdir)

if __name__ == '__main__':
  link = "magnet:?xt=urn:btih:9f89fbce75a3c7821ec0a09d60f4896a963ab1e4&dn=Doctor Who 2005 S11E01 iP WEB-DL AAC2 0 H 264-ViSUM[TGx]&tr=udp://tracker.leechers-paradise.org:6969&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://tracker.opentrackr.org:1337&tr=udp://tracker.pirateparty.gr:6969&tr=udp://eddie4.nl:6969"
  # link = "magnet:?xt=urn:btih:e84213a794f3ccd890382a54a64ca68b7e925433&dn=ubuntu-18.04.1-desktop-amd64.iso"
  magnet2torrent(link)