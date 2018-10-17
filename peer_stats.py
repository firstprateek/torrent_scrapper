import libtorrent as lt
import tempfile
import shutil
import sys
from time import sleep

TORRENT_CREATE_TIMEOUT = 60 # seconds
TORRENT_DONWLOAD_LOOPS = 12 #each loop is 5 sec

def magnet2torrent(magnet):
  tempdir = tempfile.mkdtemp()
  ses = lt.session()
  torrent_data = {}

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

  magnet_info = lt.parse_magnet_uri(magnet)
  torrent_data['trackers'] = magnet_info['trackers']
  torrent_data['info_hash'] = magnet_info['info_hash']
  torrent_name = magnet_info['name']

  handle = lt.add_magnet_uri(ses, magnet, params)
  

  try:
    print("{0}: ".format(torrent_name))
    print("Downloading Metadata (this may take a while)")
    
    time_spent_converting = 0
    while (not handle.has_metadata()):
      if time_spent_converting >= TORRENT_CREATE_TIMEOUT:
        clean_up_before_abort("Failed to convert magent link -- aborting")
        return None
      sleep(1)
      time_spent_converting += 1

    torinfo = handle.get_torrent_info()
    info_list = ['name', 'total_size', 'piece_length', 'num_pieces', 'num_files', 'metadata_size']
    for info_name in info_list: torrent_data[info_name] = getattr(torinfo, info_name)()

    print("Done downloading meta data")
    print("Starting to download torrent ...")

    handle.set_upload_limit(0) #DO NOT UPLOAD ANYTHING

    peer_info_list = {}
    def update_ip_results(peer_list):
      for peer in peer_list:
        if peer.ip in peer_info_list:
          peer_in_hash = peer_info_list[peer.ip]
          peer_in_hash['up_speed'] = max(peer_in_hash['up_speed'], peer.up_speed)
          peer_in_hash['down_speed'] = max(peer_in_hash['down_speed'], peer.down_speed)
        else:
          peer_info_list[peer.ip] = { 'up_speed': peer.up_speed, 'down_speed': peer.down_speed }

    counter = 0
    while (not handle.is_seed() and counter < TORRENT_DONWLOAD_LOOPS):
      print("counter: {0}".format(counter))
      counter += 1

      peer_list = handle.get_peer_info()
      update_ip_results(peer_list)
      if len(peer_info_list) > 1: break

      sleep(5)

    torrent_data['peer_info'] = [
      { 
        'ip': key,
        'down_speed': value['down_speed'],
        'up_speed': value['up_speed']
      } for key, value in peer_info_list.iteritems()
    ]
  except KeyboardInterrupt:
    clean_up_before_abort('Keyboard Interrupt Triggered')
    return

  print("Downloading stopped as peer data gathered ...")

  print("\nTORRENT INFO: {0} \n".format(torrent_data))
  print("Done info gathered ...\n\n")
  ses.pause()
  ses.remove_torrent(handle)
  shutil.rmtree(tempdir)

  return torrent_data

if __name__ == '__main__':
  link = "magnet:?xt=urn:btih:9f89fbce75a3c7821ec0a09d60f4896a963ab1e4&dn=Doctor Who 2005 S11E01 iP WEB-DL AAC2 0 H 264-ViSUM[TGx]&tr=udp://tracker.leechers-paradise.org:6969&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://tracker.opentrackr.org:1337&tr=udp://tracker.pirateparty.gr:6969&tr=udp://eddie4.nl:6969"
  # link = "magnet:?xt=urn:btih:e84213a794f3ccd890382a54a64ca68b7e925433&dn=ubuntu-18.04.1-desktop-amd64.iso"
  magnet2torrent(link)