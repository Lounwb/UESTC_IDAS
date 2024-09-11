# -*- coding = utf-8 -*-
"""
@Time :2024/8/14 15:42
@Author: Lounwb
@File : account.py
"""
import cv2
import time
import requests
import execjs
import base64
import logging

import utils

import numpy as np

from PIL import Image
from enum import Enum
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AccountStatus(Enum):
    unsign_in = 0
    invalid_account = 1
    incorrect_account = 2
    sign_in = 3


encrypt = execjs.compile(open('./encrypt.js', 'r', encoding='utf-8').read())

urls = {
    "login": "https://idas.uestc.edu.cn/authserver/login",
    "checkNeedCaptcha": "https://idas.uestc.edu.cn/authserver/checkNeedCaptcha.htl",
    "openSliderCaptcha": "https://idas.uestc.edu.cn/authserver/common/openSliderCaptcha.htl",
    "verifySliderCaptcha": "https://idas.uestc.edu.cn/authserver/common/verifySliderCaptcha.htl",
    "toSliderCaptcha": "https://idas.uestc.edu.cn/authserver/common/toSliderCaptcha.htl",
    "index": "https://idas.uestc.edu.cn/personalInfo/UserOnline/user/queryUserOnline",

    "queryUserOnline": "https://idas.uestc.edu.cn/personalInfo/UserOnline/user/queryUserOnline",
    "removeUserOnline": "https://idas.uestc.edu.cn/personalInfo/UserOnline/user/removeUserOnline",
    "logout": "https://idas.uestc.edu.cn/personalInfo/logout"
}

class UestcAccount:
    """Uestc IDAS Account
    1. checkNeedCapcha
    2.

    """

    def __init__(self, username, password):
        self.account_status = AccountStatus.unsign_in
        self.username = username
        self.password = password
        self.timestap = 0
        self.base_url = "https://idas.uestc.edu.cn/authserver/"
        self.userinfo = None
        self.cookies = {
            'route': None,
            'JSESSIONID': None,
            'WIS_PER_ENC': None
        }

        self.session = requests.Session()
        self.session_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstdr',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'Host': 'idas.uestc.edu.cn',
            'See-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
        self.session.headers.update(self.session_headers)
        self.__update_cookies()

    def __get_login_info(self):

        response = self.session.get(self.base_url + "login")
        self.timestap = int(time.time() * 1000)

        assert response.status_code == 200

        set_cookie = response.headers['Set-Cookie'].split(' ')
        route = set_cookie[0].split("=")[1].strip()[:-1]
        JSESSIONID = set_cookie[2].split("=")[1].strip()[:-1]
        self.__update_cookies(route=route, JSESSIONID=JSESSIONID)

        soup = BeautifulSoup(response.text, 'html.parser')
        username_pwd_login_form = soup.find(id="pwdFromId")

        _event_id = username_pwd_login_form.find(id='_eventId').get('value')
        cllt = username_pwd_login_form.find(id='cllt').get('value')
        dllt = username_pwd_login_form.find(id='dllt').get('value')
        lt = username_pwd_login_form.find(id='lt').get('value')
        execution = username_pwd_login_form.find(id='execution').get('value')

        pwd_encrypt_salt = soup.find(id='pwdEncryptSalt').get('value')

        return _event_id, cllt, dllt, lt, execution, pwd_encrypt_salt

    def __update_cookies(self, in_place=False, **kwargs):
        base = "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN"

        if kwargs is not None:
            if in_place:
                for key, value in kwargs.items():
                    self.cookies[key] = value
            else:
                for key, value in kwargs.items():
                    if key not in self.cookies or self.cookies[key] == None:
                        self.cookies[key] = value 

        self.session.headers['Cookie'] = ''.join([f"{key}={value}; " for key, value in self.cookies.items() if value]) + base

    def need_capcha(self):
        params = {
            'username': self.username,
            '_': self.timestap
        }
        self.timestap += 1

        response = self.session.get(
            self.base_url +
            "checkNeedCaptcha.htl",
            params=params)
        assert response.status_code == 200

        is_need = response.json()['isNeed']

        return is_need

    def __get_captcha(self):
        open_slider_captcha_params = {
            '_': self.timestap
        }
        self.timestap += 1

        captcha = self.session.get(
            self.base_url + "common/openSliderCaptcha.htl",
            params=open_slider_captcha_params)

        bigImage = captcha.json()['bigImage']
        smallImage = captcha.json()['smallImage']
        tagWidth = captcha.json()['tagWidth']
        yHeight = captcha.json()['yHeight']

        distance, k = utils.get_horizontal_distance(bigImage)

        return distance, k

    def __verify_captcha(self):

        error_code = 0

        def do_verify_captcha(moveLength):
            data = {
                'canvasLength': '280',
                'moveLength': moveLength
            }
            response = self.session.post(
                self.base_url +
                "common/verifySliderCaptcha.htl",
                data=data)
            return response.json()

        while error_code != 1:
            moveLength, k = self.__get_captcha()
            if k == 27:
                logging.info("[CAPTCHA] 用户取消")
                break

            json = do_verify_captcha(moveLength)
            print(json)
            error_code = json['errorCode']
            error_message = json['errorMsg']
            if error_code == 0:
                logging.error(f"[CAPTCHA {error_message}] 滑块验证码验证错误，请重试")
            elif error_code == 1:
                logging.info(f"[CAPTCHA {error_message}] 滑块验证码验证成功")
                break

    def __do_login(self, _event_id, cllt, dllt, lt,
                   execution, encrpyt_password, params=None, captcha=''):
        data = {
            'username': self.username,
            'password': encrpyt_password,
            'captcha': captcha,
            '_eventId': _event_id,
            'cllt': cllt,
            'dllt': dllt,
            'lt': lt,
            'execution': execution,
        }

        # self.session.headers['Referer'] = self.base_url + "login"
        # self.session.headers['Origin'] = 'https://idas.uestc.edu.cn'
        # self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # self.session.headers['Sec-Fetch-Site'] = 'same-origin'

        response = self.session.post(
            self.base_url + "login",
            data=data,
            params=params)
        
        if response.status_code != 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            error_message = soup.find(id='showErrorTip').text
            logging.error(error_message)
        else:
            self.account_status = AccountStatus.sign_in
            set_cookie = response.headers['Set-Cookie'].split(' ')

            route = set_cookie[0].split("=")[1].strip()[:-1]
            JSESSION = set_cookie[2].split("=")[1].strip()[:-1]
            wis_per_enc = set_cookie[5].split("=")[1].strip()[:-1]
            refernce_token = set_cookie[7].strip()

            return route, JSESSION, wis_per_enc, refernce_token

    def eportal(self, url, method='get'):
        eprotal_params = {
            'service': 'https://eportal.uestc.edu.cn/login?service=https://eportal.uestc.edu.cn/new/index.html?browser=no'
        }

        if self.account_status != AccountStatus.sign_in:
            logging.error("[LOGIN] 请先登录")
            self.login(params=eprotal_params)

        eprotal_response = self.session.get(
            'https://eportal.uestc.edu.cn/login', params=eprotal_params)
        
        print(eprotal_response.text)
        
        

    def login(self, params=None):
        """

        Args:
            _event_id (str): _description_
            cllt (str): _description_
            dllt (str): _description_
            lt (str): empty string
            execution (str): _description_
            pwd_encrypt_salt (str): _description_
        """
        _event_id, cllt, dllt, lt, execution, pwd_encrypt_salt = self.__get_login_info()
        encrpyt_password = encrypt.call(
            'encryptPassword', self.password, pwd_encrypt_salt)
        need_captcha = self.need_capcha()

        if need_captcha:
            logging.info("[LOGIN] 需要滑动验证码")

            to_slider_captcha = self.session.get(
                self.base_url + "common/toSliderCaptcha.htl")
            soup = BeautifulSoup(to_slider_captcha.text, 'html.parser')
            verify_message = soup.find(class_="text_ellipsis").text

            logging.info("[LOGIN-CAPTCHA] " + verify_message)

            self.__verify_captcha()

        route, JSESSIONID, wis_per_enc, refernce_token = self.__do_login(
            _event_id,
            cllt,
            dllt,
            lt,
            execution,
            encrpyt_password)
        
        self.__update_cookies(WIS_PER_ENC=wis_per_enc)
            
        self.session.headers['Refertoken'] = refernce_token
 
        query_params = {
            't': self.timestap
        }
        self.timestap += 1

        # query_user_online = self.session.get(urls['queryUserOnline'], params=query_params).json()
        query_user_online = self.session.get(urls['queryUserOnline'], params=query_params).json()
        self.userinfo = query_user_online['datas']['userOnline'][-1]


        logging.info(f"[LOGIN 登陆成功]  登陆地点: {self.userinfo['ipAddress']} 登陆时间: {self.userinfo['logintimeStr']}")
    
    def logout(self):

        logout_response = self.session.post(urls['logout'])

        logging.info(f"[QUIT] 用户id: {self.userinfo['id']} 退出登录成功")


if "__main__" == __name__:
    account = UestcAccount("your_id", "your_password")
    # account.login()
    account.eportal('https://idas.uestc.edu.cn/personalInfo/common/language/getLanguageTypes', method='post')
    print(account.userinfo)
    account.logout()


