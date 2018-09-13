# -*- coding: utf-8 -*-
import requests
import html2text
import click
#from http import cookiejar  
# Python 2: 
import cookielib as cookiejar

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

URL_PALADAR = 'https://paladar.cat/'
SLACK_URL = 'https://hooks.slack.com/services/'


def get_paladar_menu(channel, message):
    s = requests.Session()
    s.cookies.set_policy(BlockAll())
    r = s.get(
        URL_PALADAR,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                        'AppleWebKit/537.36 (KHTML, like Gecko)'
                        ' Chrome/39.0.2171.95 Safari/537.36',
    })
    menu = r.text.split('<tbody')[1][1:]
    menu = html2text.html2text(menu)
    menu = ''.join(menu.split('|')[1:-1])
    mlines = [l.strip() for l in menu.split('\n')]
    mlines[0] += '\n'
    for l in mlines:
        if l and l[0] != '*':
            mlines[mlines.index(l)] = '# ' + l
    menu = '\n'.join(mlines)
    return menu


def post_slack_text(text, url):
    hdrs = {
        'Content-type': 'application/json'
    }
    pyld = {
        'text': text,
        'markdown': True
    }
    r = requests.post(url, headers=hdrs, payload=pyld)
    if r.status_code == 200:
        print('OK')
    else:
        print('Failed to send to Slack: {}'.format(r.status_code))
        r.raise_for_status()


@click.command()
@click.option(
    '-s', '--slack', type=str, default='', help='Slack app URL to post menu')
def mel(slack):
    menu = get_paladar_menu()
    if not slack:
        print(menu)
        exit()
    if SLACK_URL not in slack:
        slack = SLACK_URL + slack
    post_slack_text(menu, slack)

if __name__ == '__main__':
    mel()
