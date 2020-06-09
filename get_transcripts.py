from bs4 import BeautifulSoup
from urllib.request import urlopen

def scrape_episode(ep_num):
    """
    Scrape an episode transcript from avatarspirit.net and parse it into a plaintext format,
    which only contains dialogue. Each line is of the form [Character: spoken dialogue]. 
    """
    url = f'http://atla.avatarspirit.net/transcripts.php?num={ep_num}'
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), features='lxml')
    script_text = ' '.join([
        t for line in soup.find('blockquote').children \
        if (t:=(str(line).strip().replace('\r', '').replace('</b>', '') \
        if line.name=='b' or not hasattr(line, 'get_text') else line.get_text()))
    ])
    script_lines = script_text.split('<b>')
    return (f'{l.strip()}\n' for l in script_lines)

# Scrape all episodes and write each to a file
for season in range(1, 4):
    for episode in range(1, 21):
        ep_num = f'{season}{str(episode).zfill(2)}'
        script_lines = scrape_episode(ep_num)
        with open(f'transcripts/{ep_num}.txt', mode='w') as f:
            f.writelines(script_lines)