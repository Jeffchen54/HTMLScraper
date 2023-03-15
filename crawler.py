import re
import requests
from bs4 import BeautifulSoup
import os
import queue
import argparse
import time

HEADERS = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}

def read_urls(urls:str)->queue.Queue:
    """
    Returns a list of urls read from a file containing
    1 url per line

    Args:
        urls (str): file with urls to 

    Pre: urls exists
    Returns:
        Queue: Queue of urls
    """
    q = queue.Queue()
    with open(urls, "r") as fd:
        for line in fd:
            q.put_nowait(line.rstrip())
    
    return q

def read_all_lines(path:str, lower:bool=True)->list[str]:
    """
    Reads all lines from a file and places them in a list

    Args:
        path (str): path of file to read
        lower (bool): Convert keywords to lower case

    Returns:
        list[str]: list of lines from the file
    """
    lines = []
    with open(path, 'r') as fd:
        for line in fd:
            lines.append(line if not lower else line.lower())
    return lines
    
def get_urls_from_html(html:str, key_words:list[str])->list[str]:
    """
    Returns a list of urls from an html whose plaintext contains 
    key words from key_words

    Args:
        html (str): HTML to parse
        key_words (list[str]): list of key words

    Returns:
        list[str]: List of extracted urls.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    links = []
    for link in soup.find_all('a'):
        if link.get('href') and link.get('href').startswith("https") and len(words_in_string(key_words, link.text.lower())) > 0:
            links.append(link.get('href'))
        
    return links

def words_in_string(word_list:list[str], a_string:str)->set:
    """
    Intersect word_list with a a_string and return the result
    
    Args:
        word_list (list[str]): List of keywords
        a_string (str): String to intersect with keywords

    Returns:
        set: set of intersected strings
    """
    return set(word_list).intersection(a_string.split())
    
def save_text(text:str, fname:str)->None:
    """
    Saves text to a file

    Args:
        text (str): Text to save
        fname: (str): name of file absolute path to save text to, will 
                    override local files with the same name
    """
    with open(fname, 'w', encoding='utf-8') as fd:
        fd.write(text)

def extract_from_urls(urls:queue.Queue, folder:str, max_limit:int, key_words:list[str])->list[str]:
    """
    Extract html plaintext recursively from a list of urls in FIFO order.

    Args:
        urls (list[str]): List of initial urls
        folder (str): Where to store html plaintext
        max_limit (int): Maximum number of urls to scrape
    Returns: list of all crawled urls
    """
    extraction_count = 0
    processed_urls = set()
    while extraction_count < max_limit and urls.qsize() > 0:
        try:
            # Get URL at front
            url = urls.get_nowait()
            
            # Request URL
            req = requests.get(url, headers=HEADERS, timeout=5)
            
            # Write response to file
            soup = BeautifulSoup(req.text, "html.parser")
            save_text(str(soup.prettify()), os.path.join(folder, re.sub(r'[^\w\-_\. ]|[\.]$', ' ', url) + '.html'))
            
            # Get a list of urls from the html
            related_urls = get_urls_from_html(req.text, key_words)
            
            # Add URLs to the Queue
            for url in related_urls:
                prev = len(processed_urls)
                # Add url to processed list
                processed_urls.add(url)
                # If processed url size does not increase, is a dupe and is not enqueued
                if prev != len(processed_urls):
                    urls.put_nowait(url)
            
            # Increment extraction count
            extraction_count += 1
            print("Processed {}".format(url))
            # Prevent rate limiting
            time.sleep(5)
        except requests.exceptions as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
    

def main()->None:
    """
    Web scraper runner
    """
    # Build commandline args
    parser = argparse.ArgumentParser(
                    prog='crawler.py',
                    description='Saves HTML from a list of given URLs',
                    epilog='Author: Chenjeff4840\t\tLast modified: 3/14/2023')
    
    parser.add_argument('-f', '--folder', help="Folder to save HTML files to", required=True, dest='folder')
    parser.add_argument('-l', '--links', help="Text file containing a list of links", required=True, dest='links')
    parser.add_argument('-k', '--keywords', help="Text file containing 1 keyword per line for recursive link scraping", dest='keywords')
    parser.add_argument('-m', '--maxlimit', help="Maximum number of urls to parse", dest='limit', type=int, default=100)
    
    # Get cmd args as dict
    args = vars(parser.parse_args())
    
    # Get URLs
    urls = read_urls(args['links'])
    
    # Call URL extractor
    extract_from_urls(urls, args['folder'], args['limit'], read_all_lines(args['keywords']) if args['keywords'] else [])

if __name__ == "__main__":
    main()