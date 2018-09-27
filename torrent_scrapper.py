from bs4 import BeautifulSoup
import requests
from subprocess import call
import csv

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
	with open('torrent_data_tv.csv', 'w', newline='') as myfile:
		torrent_writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		torrent_data = []
		# print('name, magnet_link, Size, File, Age, Seed, Leech, Type')
		torrent_writer.writerow(['name', 'magnet_link', 'Size', 'File', 'Age', 'Seed', 'Leech', 'Type'])
		
		for i in range(1, 101):
			r = requests.get(f'{url}{i}' if i > 1 else url, headers=headers)

			# check the status code of the response to make sure the request went well
			if r.status_code != 200:
				print("request denied")
				return
				# print("scraping " + f'{url}{i}')

			# convert the plaintext HTML markup into a DOM-like structure that we can search
			soup = BeautifulSoup(r.text, 'html.parser')

			torrent_table = soup.find_all('table', class_="table table--bordered table--striped table--hover torrents_table")[0]
			for tr_tag in torrent_table.tbody.find_all('tr'):
				current_torrent_hash = {}
				current_torrent_hash['type'] = 'TV'
				name = str.strip(tr_tag.find_all('a', class_='torrents_table__torrent_title')[0].string)
				current_torrent_hash['name'] = name

				magnet_link = tr_tag.find_all('div', class_='torrents_table__actions')[0].find_all('a')[2]['href']
				current_torrent_hash['magnet_link'] = magnet_link

				for index, td_tag in enumerate(tr_tag.find_all('td')):
					if index == 0: continue
					current_torrent_hash[td_tag['data-title']] = str.strip(td_tag.string)

				# print(f'{name}, {magnet_link}, {current_torrent_hash["Size"]}, {current_torrent_hash["Files"]}, {current_torrent_hash["Age"]}, {current_torrent_hash["Seed"]}, {current_torrent_hash["Leech"]}')
				torrent_writer.writerow([name, magnet_link, current_torrent_hash["Size"], current_torrent_hash["Files"], current_torrent_hash["Age"], current_torrent_hash["Seed"], current_torrent_hash["Leech"], 'Tv'])
				# torrent_data.append(current_torrent_hash)
				# call(['open', magnet_link])
		# print(torrent_data)


scrapping()