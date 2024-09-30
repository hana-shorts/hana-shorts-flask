# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:57:19 2023

@author: Administrator
"""

import time, copy
import yaml
import requests
import json

import asyncio

import os

import pandas as pd

from collections import namedtuple
from datetime import datetime

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32

config_root = 'D:\\pycharm-workspace\\trade\\'
token_tmp = config_root + 'KIS_PAPER' + datetime.today().strftime("%Y%m%d")

if os.path.exists(token_tmp) == False:
    f = open(token_tmp, "w+")

with open(config_root + 'kis_devlp.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

_TRENV = tuple()
_last_auth_time = datetime.now()
_autoReAuth = False
_DEBUG = False
_isPaper = True

_base_headers = {
    "Content-Type": "application/json",
    "Accept": "text/plain",
    "charset": "UTF-8",
    'User-Agent': _cfg['my_agent']
}

def save_token(my_token, my_expired):
    valid_date = datetime.strptime(my_expired, '%Y-%m-%d %H:%M:%S')
    with open(token_tmp, 'w', encoding='utf-8') as f:
        f.write(f'token: {my_token}\n')
        f.write(f'valid-date: {valid_date}\n')

def read_token():
    try:
        with open(token_tmp, encoding='UTF-8') as f:
            tkg_tmp = yaml.load(f, Loader=yaml.FullLoader)

        exp_dt = datetime.strftime(tkg_tmp['valid-date'], '%Y-%m-%d %H:%M:%S')
        now_dt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        if exp_dt > now_dt:
            return tkg_tmp['token']
        else:
            return None
    except Exception as e:
        return None

def _getBaseHeader():
    if _autoReAuth: reAuth()
    return copy.deepcopy(_base_headers)

def _setTRENV(cfg):
    nt1 = namedtuple('KISEnv', ['my_app', 'my_sec', 'my_acct', 'my_prod', 'my_token', 'my_url'])
    d = {
        'my_app': cfg['my_app'],
        'my_sec': cfg['my_sec'],
        'my_acct': cfg['my_acct'],
        'my_prod': cfg['my_prod'],
        'my_token': cfg['my_token'],
        'my_url': cfg['my_url']
    }
    global _TRENV
    _TRENV = nt1(**d)

def isPaperTrading():
    return _isPaper

def changeTREnv(token_key, svr='vps', product=_cfg['my_prod']):
    cfg = dict()

    cfg['my_app'] = _cfg['paper_app']
    cfg['my_sec'] = _cfg['paper_sec']

    if svr == 'vps' and product == '01':
        cfg['my_acct'] = _cfg['my_paper_stock']
    elif svr == 'vps' and product == '03':
        cfg['my_acct'] = _cfg['my_paper_future']

    cfg['my_prod'] = product
    cfg['my_token'] = token_key
    cfg['my_url'] = _cfg[svr]

    _setTRENV(cfg)


def _getResultObject(json_data):
    _tc_ = namedtuple('res', json_data.keys())

    return _tc_(**json_data)


def auth(svr='vps', product=_cfg['my_prod'], url=None):
    p = {
        "grant_type": "client_credentials",
    }
    p["appkey"] = _cfg['paper_app']
    p["appsecret"] = _cfg['paper_sec']

    saved_token = read_token()
    if saved_token is None:
        url = f'{_cfg[svr]}/oauth2/tokenP'
        res = requests.post(url, data=json.dumps(p), headers=_getBaseHeader())
        rescode = res.status_code
        if rescode == 200:
            my_token = _getResultObject(res.json()).access_token
            my_expired= _getResultObject(res.json()).access_token_token_expired
            save_token(my_token, my_expired)
        else:
            print('Get Authentification token fail!\nYou have to restart your app!!!')
            return
    else:
        my_token = saved_token

    changeTREnv(f"Bearer {my_token}", svr, product)

    _base_headers["authorization"] = _TRENV.my_token
    _base_headers["appkey"] = _TRENV.my_app
    _base_headers["appsecret"] = _TRENV.my_sec

    global _last_auth_time
    _last_auth_time = datetime.now()

    if (_DEBUG):
        print(f'[{_last_auth_time}] => get AUTH Key completed!')

def reAuth(svr='vps', product=_cfg['my_prod']):
    n2 = datetime.now()
    if (n2 - _last_auth_time).seconds >= 86400:
        auth(svr, product)

def getEnv():
    return _cfg

def getTREnv():
    return _TRENV

def set_order_hash_key(h, p):
    url = f"{getTREnv().my_url}/uapi/hashkey"

    res = requests.post(url, data=json.dumps(p), headers=h)
    rescode = res.status_code
    if rescode == 200:
        h['hashkey'] = _getResultObject(res.json()).HASH
    else:
        print("Error:", rescode)

class APIResp:
    def __init__(self, resp):
        self._rescode = resp.status_code
        self._resp = resp
        self._header = self._setHeader()
        self._body = self._setBody()
        self._err_code = self._body.msg_cd
        self._err_message = self._body.msg1

    def getResCode(self):
        return self._rescode

    def _setHeader(self):
        fld = dict()
        for x in self._resp.headers.keys():
            if x.islower():
                fld[x] = self._resp.headers.get(x)
        _th_ = namedtuple('header', fld.keys())

        return _th_(**fld)

    def _setBody(self):
        _tb_ = namedtuple('body', self._resp.json().keys())

        return _tb_(**self._resp.json())

    def getHeader(self):
        return self._header

    def getBody(self):
        return self._body

    def getResponse(self):
        return self._resp

    def isOK(self):
        try:
            if (self.getBody().rt_cd == '0'):
                return True
            else:
                return False
        except:
            return False

    def getErrorCode(self):
        return self._err_code

    def getErrorMessage(self):
        return self._err_message

    def printAll(self):
        print("<Header>")
        for x in self.getHeader()._fields:
            print(f'\t-{x}: {getattr(self.getHeader(), x)}')
        print("<Body>")
        for x in self.getBody()._fields:
            print(f'\t-{x}: {getattr(self.getBody(), x)}')

    def printError(self, url):
        print('-------------------------------\nError in response: ', self.getResCode(), ' url=', url)
        print('rt_cd : ', self.getBody().rt_cd, '/ msg_cd : ',self.getErrorCode(), '/ msg1 : ',self.getErrorMessage())
        print('-------------------------------')

def _url_fetch(api_url, ptr_id, tr_cont, params, appendHeaders=None, postFlag=False, hashFlag=True):
    url = f"{getTREnv().my_url}{api_url}"

    headers = _getBaseHeader()

    tr_id = ptr_id
    if ptr_id[0] in ('T', 'J', 'C'):
        if isPaperTrading():
            tr_id = 'V' + ptr_id[1:]

    headers["tr_id"] = tr_id
    headers["custtype"] = "P"
    headers["tr_cont"] = tr_cont

    if appendHeaders is not None:
        if len(appendHeaders) > 0:
            for x in appendHeaders.keys():
                headers[x] = appendHeaders.get(x)

    if (_DEBUG):
        print("< Sending Info >")
        print(f"URL: {url}, TR: {tr_id}")
        print(f"<header>\n{headers}")
        print(f"<body>\n{params}")

    if (postFlag):
        res = requests.post(url, headers=headers, data=json.dumps(params))
    else:
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        ar = APIResp(res)
        if (_DEBUG): ar.printAll()
        return ar
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None
