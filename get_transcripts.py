from time import sleep
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

def scrape_episode(ep_code: int) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Scrape an episode transcript from avatarspirit.net and parse it into a plaintext format,
    which only contains dialogue. Each line is of the form [Character: spoken dialogue]. 
    """
    url = f'https://transcripts.foreverdreaming.org/viewtopic.php?f=574&t={ep_code}'
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), features='lxml')
    if not (ep_num := get_ep_num(soup)):
        return None, None
    return clean_transcript(soup), ep_num

def get_ep_num(script_soup: BeautifulSoup) -> Optional[str]:
    """Return the season and episode number as a string, e.g. 02x13."""
    header = script_soup.find('div', class_='t-header')
    ep_num_and_name = header.find('a').get_text()
    print(ep_num_and_name)
    # Special content
    if 'Deleted Scenes' in ep_num_and_name or 'x00' in ep_num_and_name:
        return
    ep_num = ep_num_and_name[:ep_num_and_name.find('-')].strip()
    # More special content
    special_episodes = ['05x29', '05x30']
    if ep_num in special_episodes:
        return
    # Two combined episodes
    ep_num = ep_num.replace('/', '-')
    return ep_num

def clean_transcript(script_soup: BeautifulSoup):
    """Strip out everything but dialogue and character names and return a list of lines."""
    script_lines = [l.get_text() for l in script_soup.find('div', class_='postbody').find_all('p')]
    script_lines = [
        re.sub('([\(\[]).*?([\)\]])', '',           # Remove all text in parens/brackets
        re.sub(r'\([^()]*\)', '', line))            # Sometimes it's even doubly nested
        .replace('(', '').replace(')', '')          # Sometimes they forget to properly close parens...
        .strip() for line in script_lines
    ]
    script_lines = [l.replace(':', '::', 1) for l in script_lines]
    return (f'{l.strip()}\n' for l in script_lines)

# Scrape all episodes and write each to a file
MIN_EP_CODE = 25301
MAX_EP_CODE = 25498
for ep_code in range(MIN_EP_CODE, MAX_EP_CODE + 1):
    script_lines, ep_num = list(scrape_episode(ep_code))
    if not ep_num:
        continue
    with open(f'transcripts/{ep_num}.txt', mode='w') as f:
        f.writelines(script_lines)
    assert sum(l.count('::') for l in script_lines) == len(list(script_lines))
    sleep(2)