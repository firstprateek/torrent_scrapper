from bs4 import BeautifulSoup
import requests
import subprocess
import csv
import bencode

# soup = BeautifulSoup(html_doc, 'html.parser')
#url = "https://katcr.co/category/movies/page/"
url = "https://katcr.co/category/tv/page/"
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

def scrapping():
        with open('torrent_data_tv.csv', 'wb') as myfile:
                torrent_writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                torrent_data = []
                # print('name, magnet_link, Size, File, Age, Seed, Leech, Type')
                torrent_writer.writerow(['name', 'magnet_link', 'Size', 'File', 'Age', 'Seed', 'Leech', 'Type'])
                
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
                        for link in soup.find_all('a'):
                                if not link['href'].startswith("magnet"): continue
                                counter+=1
                                print(link)
                                torrent_file = subprocess.check_output(['python', 'Magnet_To_Torrent2.py', '-m', "%s" %(link['href']), '-o', "torrent%s" %(counter)])
                                rawdata = open("torrent%s" %(counter)).read()
                                metadata = bencode.bdecode(rawdata)
                                print(metadata)
                                break


                        print("counter = %s" %(counter))

scrapping()