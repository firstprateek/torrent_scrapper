# Torrent Scapper

A command line tool that scrapes magnet links, converts magnet links in to .torrent files and then writes the meta data for the torrents into csv.

### This project is W.I.P.

## Requirements
* python
* python-libtorrent (libtorrent-rasterbar version 0.16 or later)

## Install python-libtorrent on Ubuntu
`sudo apt-get install python-libtorrent -y`

## Install python-libtorrent on macOS
`brew install libtorrent-rasterbar --with-python`

## Install python-libtorrent on Fedora
`sudo dnf install rb_libtorrent-python2`

## Config

#### Process Count
Number of sub-processes to run. These sub-processes parallelize the conersion of magnet links to .torrent files.

#### Time out Sec
Time out in seconds for the subprocess mentioned above.

#### Headers
HTTP headers used by the request library when making the request for the page to scape.

#### CSV name
Name of the ouput csv.

#### Default NA value
Placeholder for null values in the output csv.

#### URL list
List of urls to scrape.
