from bs4 import BeautifulSoup
import requests
from subprocess import Popen, PIPE
import csv
import bencode
from multiprocessing import Pool
from threading import Timer
import os

# soup = BeautifulSoup(html_doc, 'html.parser')
#url = "https://katcr.co/category/movies/page/"
url = "https://katcr.co/category/tv/page/"
process_count=5
timeout_sec=30
process_status={}
# spoof some headers so the request appears to be coming from a browser, not a bot

headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "cache-control": "max-age=0",
                "connection": "keep-alive",
                "cookie": "KATSSESS_ID70AT=v9mf684tkqt96en13q4p540m75govqn0",
                "host": "katcr.co",
                "upgrade-insecure-requests": "1",
}

def kill_and_set_flag(proc, id):
  proc.kill
  process_status[id] = 1
  print("%s killed" %(id))

def convert_magnet_to_torrent(link_tag):
        torrent_file_name = "torrent%s" %(os.getpid())
        print("started: %s" %(torrent_file_name))

        proc = Popen(['python', 'Magnet_To_Torrent2.py', '-m', "%s" %(link_tag['href']), '-o', torrent_file_name], stdout=PIPE, stderr=PIPE)
        timer = Timer(timeout_sec, kill_and_set_flag, [proc, torrent_file_name])
        result = []
        try:
                timer.start()
                stdout, stderr = proc.communicate()
                # subprocess.check_output()
                rawdata = open(torrent_file_name).read()
                print("completed: %s" %(torrent_file_name))
                result = bencode.bdecode(rawdata)
        finally:
                timer.cancel()
                Popen(['rm', torrent_file_name], stdout=PIPE, stderr=PIPE)
                if torrent_file_name in process_status and process_status[torrent_file_name] == 1:
                        del process_status[torrent_file_name]
                        return None
                else:
                        return result

def scrapping():
        with open('torrent_data.csv', 'wb') as myfile:
                torrent_writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                torrent_data = []
                # print('name, magnet_link, Size, File, Age, Seed, Leech, Type')
                torrent_writer.writerow(['creation date', 'announce', 'files', 'piece length', 'name', 'announce-list'])
                
                for i in range(1, 2):
                        r = requests.get("%s%s" %(url, i) if i > 1 else url, headers=headers)

                        # check the status code of the response to make sure the request went well
                        if r.status_code != 200:
                                print("request denied")
                                return
                                # print("scraping " + f'{url}{i}')

                        # convert the plaintext HTML markup into a DOM-like structure that we can search
                        soup = BeautifulSoup(r.text, 'html.parser')

                        counter = 0;
                        links = [link for link in soup.find_all('a') if link['href'].startswith('magnet')]

                        # chunk_result = []
                        for i in range(0, len(links), process_count):
                                chunk = links[i:i+process_count]
                                pool = Pool(processes=process_count)
                                chunk_result = pool.map(convert_magnet_to_torrent, chunk)
                                chunk_result = [chunk for chunk in chunk_result if chunk != None]

                                print('strat with loop 5 xxxxxxxxxxxxx')
                                for result in chunk_result:
                                        # print(result)
                                        torrent_writer.writerow([result['creation date'], result['announce'], result['info']['files'], result['info']['name'], result['announce-list']])
                                
                                print('done with loop 5 xxxxxxxxxxxxx')

                        # for result in chunk_result:
                        #         print(result['info']['files'][0]['path'][0])

                        

if __name__ == '__main__':
        scrapping()
