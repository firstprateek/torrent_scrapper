from bs4 import BeautifulSoup
import requests
from subprocess import Popen, PIPE
import csv
import bencode
import json
from multiprocessing import Pool
from threading import Timer
import os
import signal

process_status={}
CONFIG = {}
processes_completed = 0
#CONFIG SETTINGS
with open("config.json") as jsonfile:
  CONFIG = json.load(jsonfile)

def check_key(dictionary, key):
  return dictionary[key] if key in dictionary else CONFIG['default_na_value']

def kill_and_set_flag(proc, id):
  os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
  process_status[id] = 1
  print("%s killed" %(id))

def convert_magnet_to_torrent(link_tag):
  torrent_file_name = "torrent%s" %(os.getpid())
  print("started subprocess: %s" %(torrent_file_name))
  
  proc = Popen(['python', 'Magnet_To_Torrent2.py', '-m', link_tag['href'].encode('ascii', 'ignore'), '-o', torrent_file_name], stdout=PIPE, preexec_fn=os.setsid)
  timer = Timer(CONFIG['timeout_sec'], kill_and_set_flag, [proc, torrent_file_name])
  result = []
  try:
    timer.start()
    stdout, stderr = proc.communicate()
    rawdata = open(torrent_file_name).read()
    print("completed subprocess: %s" %(torrent_file_name))
    result = bencode.bdecode(rawdata)
  finally:
    timer.cancel()
    Popen(['rm', torrent_file_name], stdout=PIPE, stderr=PIPE)
    if torrent_file_name in process_status and process_status[torrent_file_name] == 1:
      del process_status[torrent_file_name]
      return None
    else:
      return result

def scrape_page(url, csv_writer):
  global processes_completed
  response = requests.get(url['link'], headers=CONFIG['headers'])

  if response.status_code != 200:
    print("request denied")
    return

  soup = BeautifulSoup(response.text, 'html.parser')
  links = [link for link in soup.find_all('a') if link['href'].startswith('magnet')]

  for link_index in range(0, len(links), CONFIG['process_count']):
    chunk = links[link_index:link_index+CONFIG['process_count']]
    pool = Pool(processes=CONFIG['process_count'])
    chunk_result = pool.map(convert_magnet_to_torrent, chunk)
    chunk_result = [chunk for chunk in chunk_result if chunk != None]

    for idx, result in enumerate(chunk_result):
      if 'info' not in result: result['info'] = {}
      csv_writer.writerow(
        [
          check_key(result, 'creation date'),
          check_key(result, 'announce'),
          check_key(result['info'], 'files'),
          check_key(result['info'], 'piece length',),
          check_key(result['info'], 'name'),
          check_key(result, 'announce-list'),
          check_key(url, 'type'),
          links[link_index+idx]['href'].encode('ascii', 'ignore'),
          check_key(url, 'source'),
        ]
      )
    
    processes_completed += CONFIG['process_count']
    print("processes completed: %s" %(processes_completed))

if __name__ == '__main__':
  with open(CONFIG['csv_name'], 'wb') as myfile:
    csv_writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    csv_writer.writerow(
      [
        'creation date',
        'announce',
        'files',
        'piece length',
        'name',
        'announce-list',
        'type',
        'magnet link',
        'source'
      ]
    )

    for url in CONFIG['url_list']:
      if url['multi_page']:
        for i in range(1, url['pages']):
          url['link'] = "%s%s" %(url['link'], i) if i > 1 else url['link']
          scrape_page(url, csv_writer)
      else:
        scrape_page(url, csv_writer)
