#!/home/alienone/anaconda3/bin/python3
# -*- coding: utf-8 -*-


__date__ = "03.21.2015"
__author__ = "AlienOne"
__copyright__ = "MIT"
__credits__ = ["Justin Jessup"]
__license__ = "MIT"
__version__ = "0.5"
__maintainer__ = "AlienOne"
__email__ = "Justin@alienonesecurity.com"
__status__ = "Functional"


import requests
import hashlib
from clint.textui import progress
from clint.textui import colored
from os import path
from os import makedirs
from bs4 import BeautifulSoup
from functools import partial


"""Mass file Downloader for the Syrian Bluecoat data set"""


WORKING_DIR = "/media/alienone/4612-7C6E/Data/Syria"


def md5sum(filename):
    """
    MD5 Checksum value of file
    :param file_name: File
    :return: MD5 checksum
    """
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 4096), b''):
            d.update(buf)
    return d.hexdigest()


def file_size(num, suffix='B'):
    """
    Output human readable file size
    :param num: Integer in bytes
    :param suffix: Appended to type of file size
    :return: String
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def make_dirs(path_list):
    """
    Create directory tree for downloading Syrian Bluecoat data set
    :param path_list: Download file $PATHS
    :return: Directory tree if does not already exist
    """
    for path_name in path_list:
        if not path.exists(WORKING_DIR + path_name):
            makedirs(WORKING_DIR + path_name)


def get_links(url_name, tuple_suffixes):
    """
    Get URLs for file downloads
    :param url_name: S3 URL $PATH
    :param tuple_suffixes: File extension suffixes of files to be downloaded
    :return: Generator object
    """
    url_get = requests.get(url_name)
    if url_get.status_code == 200:
        soup = BeautifulSoup(url_get.text, 'lxml')
        for href_link in soup.findAll('a', href=True):
            if href_link['href'].endswith(tuple_suffixes):
                yield href_link['href']


def download_file(path_name, url):
    """
    Download remote file via HTTP protocol
    :param path_name: $PATH to file
    :param url: $ROOT URL
    :return: Downloaded file
    """
    output_filename = WORKING_DIR + path_name.split('.com')[1] + url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(output_filename, 'wb') as output_file:
        total_length = int(r.headers.get('content-length'))
        print("")
        print(colored.yellow('Downloading: ') + colored.green(url.split('/')[-1]))
        print(colored.blue('File Size: ') + colored.red(file_size(total_length, suffix='B')))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=total_length/1024+1):
            if chunk:
                output_file.write(chunk)
                output_file.flush()
    print(colored.magenta("Download Completed for: ") + colored.red(url.split('/')[-1]))
    print(colored.white("MD5 Checksum {file_name}").format(file_name=url.split('/')[-1]))
    print(colored.red("{check_sum}").format(check_sum=md5sum(output_filename)))
    print("")


def main():
    """
    Main function execution
    :return: Downloaded files to appropriate download $PATH within download tree
    """
    tuple_suffixes = ('.gz')
    path_list = ["/raw_logs/SG-42/",
                 "/raw_logs/SG-43/",
                 "/raw_logs/SG-44/",
                 "/raw_logs/SG-45/",
                 "/raw_logs/SG-46/",
                 "/raw_logs/SG-47/",
                 "/raw_logs/SG-48/"]
    url_list = ["http://project-bluesmote.s3-website-us-east-1.amazonaws.com" for x in range(0, len(path_list))]
    dict_obj = dict(zip(path_list, url_list))
    make_dirs([x for x in path_list])
    for path_name, url_name in dict_obj.items():
        path_name = url_name + path_name
        for file_to_download in get_links(path_name, tuple_suffixes):
            download_file(path_name, path_name + file_to_download)


if __name__ == '__main__':
    main()
