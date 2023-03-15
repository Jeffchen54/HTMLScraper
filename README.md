# HTMLScraper
Website archival script.
- Archives HTML only
- Supports bulk archiving
- Supports basic recursive archiving based on keywords, no scoring algorithm implemented

## Requirements
* Windows 10/11
* Python 3.9.x or higher

## Dependencies
* pip install bs4
* pip install requests

## Switches
    crawler.py [-h] -f FOLDER -l LINKS [-k KEYWORDS] [-m LIMIT]

* -h: Help
* -f FOLDER <path>: REQUIRED. Full path to folder to store HTML in
* -l LINKS <path>: REQUIRED. Full path to a file containing links to websites to archive, 1 url per line with no empty lines.
* -k KEYWORDS <path>: Full path to a file containing keywords to look for when recursively archiving, 1 keyword per line.
* -m LIMIT <int>: Maximum number of URLs to archive, default is 100

## Example Usage:
    python crawler.py --folder "D:\git projects\personal\web crawler\chenjeff4840" --links "D:\git projects\personal\web crawler\chenjeff4840\information.txt"

Output HTML to "D:\git projects\personal\web crawler\chenjeff4840". Uses seed URLs from "D:\git projects\personal\web crawler\chenjeff4840\information.txt".

## Output
Output HTML file name correspond to the website the HTML was scraped from with a single space replacing the illegal file name characters the URL has.
