# -*- Encoding: utf-8 -*-
"""
renren login
"""
import urllib
from httplib2 import Http
import os
import re


cookie_path = 'cookies'

if not os.path.exists(cookie_path):
    os.makedirs(cookie_path) 

def __full_filename(user):
    return os.path.join(cookie_path, '%s.cookie' % user)

def __save_cookie(user, cookie):
    with open(__full_filename(user), 'w') as f:
        f.write(cookie)

def __get_cookie(user):
    filename = __full_filename(user)
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        cookie = f.read()
    return cookie


headers_template = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.65 Safari/534.24',
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
}


def login(user, password, use_cache=True):
    """sigin to renren.com. return and save cookie if success."""
    # TODO:
    # 1. deal with timeout
    # 2. random useragent
    # 3. more accurate headers
    # 5. deal with verfication code and passwd error

    if use_cache:
        cookie = __get_cookie(user)
        if cookie:
            return cookie

    headers = headers_template.copy()
    # url
    url = 'http://www.renren.com/PLogin.do'
    home = 'http://www.renren.com/home'
    # body
    login_data = {
        'email': user,
        'password': password,
        'origURL': home,
        'domain': 'renren.com'
    }
    body = urllib.urlencode(login_data)

    h = Http()

    rsp, content = h.request(url, 'POST', headers=headers, body=body)  # response 302

    if rsp.get('location', None) == home:  # redirect to home if success
        headers['Cookie'] = rsp['set-cookie']
        rsp2, content = h.request(home, headers=headers)
        with open('login_success_rsp.log', 'a') as f:
            f.write(str(rsp2) + '\n\n')
        cookie = rsp2['set-cookie']
        __save_cookie(user, cookie)
        return cookie
        # request again with this cookie
    else:  # redirect to login page again if failed
        with open('login_failed_{}.html'.format(user), 'w') as f:
            f.write(content)
        return None

def renrenId(cookie):
    proj = re.compile(r'feedType=(\d+)_hot;')
    m = proj.search(cookie)
    if m is not None:
        return m.group(1)
    else:
        return None

if __name__ == '__main__':
    from settings import account
    iCookie = login(account['email'], account['password'])
    print renrenId(iCookie)
