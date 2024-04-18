import requests
import re
import execjs
import time
import json

import utils

requests = requests.Session()

class IdasUESTC():
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        self.cookies = {
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'zh_CN',
            'route': '',
            'JSESSIONID': '',
        }

        self.js = execjs.compile(open('./encrypt.js', 'r', encoding='utf-8').read())
        
    def get_salt(self):

        url = "https://idas.uestc.edu.cn/authserver/login"
        params = {}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            page = response.text
        # salt = re.findall('var pwdDefaultEncryptSalt = "(.*?)";', page)[0]
        salt = re.search(r'var pwdDefaultEncryptSalt = "([^"]+)"', page).group(1)
        lt = re.search(r'name="lt" value="([^"]+)"', page).group(1)
        execution = re.search(r'name="execution" value="([^"]+)"', page).group(1)

        route = response.cookies.get('route')
        JSESSIONID = response.cookies.get('JSESSIONID')
        
        self.cookies['route'] = route
        self.cookies['JSESSIONID'] = JSESSIONID

        return salt, lt, execution
    
    def need_capcha(self):
        url = "https://idas.uestc.edu.cn/authserver/needCaptcha.html"
        timestamp = int(time.time())
        params = {
            'username': self.username,
            'pwdEncrypt2': 'pwdEncryptSalt',
            '_': timestamp
        }
        response = requests.get(url, params=params, cookies=self.cookies)
        return response.text

    def get_capcha(self):
        need_capcha = self.need_capcha()
        if 'true' in need_capcha:
            url = "https://idas.uestc.edu.cn/authserver/sliderCaptcha.do"
            timestamp = int(time.time())
            params = {
                '_': timestamp
            }
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            bigImageNum = data['bigImageNum']
            smallImageNum = data['smallImageNum']
            smallImage = data['smallImage']
            bigImage = data['bigImage']

            distance = utils.get_horizontal_distance(bigImage)
            return distance
    def verify_capcha(self):
        sign = ''
        code = 1
        data = {}
        def get_verify(moveLength):
            url = "https://idas.uestc.edu.cn/authserver/verifySliderImageCode.do"
            params = {
                'canvasLength': 280,
                'moveLength': moveLength
            }
            response = requests.get(url, params=params, cookies=self.cookies)
            return response.text

        while code != 0:
            moveLength = self.get_capcha()
            response = get_verify(moveLength)
            data = json.loads(response)
            code = data['code']
        return sign

    def login(self, salt, lt, execution, sign):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'CASTGC=TGT-9639-iIBzfOBYn4ca7XqKWKoV2lEkOcATPLhRFi99jVV1UbiVywVBQE1713427129463-noqX-cas; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; route=c646de0d09c9aceac3feae3b5b7928b7; JSESSIONID=FL3wN9sjy4pvysftz7sUgxAAudKz3HxlyN4-XOaiI6INVLzJVwbL!-1144444691',
            'Origin': 'https://idas.uestc.edu.cn',
            'Referer': 'https://idas.uestc.edu.cn/authserver/login',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        params = { 
            'service': 'https://idas.uestc.edu.cn/authserver/services/j_spring_cas_security_check'
        }
        encrpyt_password = self.js.call('encryptAES', self.password, salt)
        url = "https://idas.uestc.edu.cn/authserver/login"
        data = {
            'username': self.username,
            'password': encrpyt_password,
            'lt': lt,
            'dllt': 'userNamePasswordLogin',
            'execution': execution,
            '_eventId': 'sumbmit',
            'rmShown': '1',
            'sign': sign
        }
        response = requests.post(url, headers=headers, params=params, data=data, cookies=self.cookies)
        print(response.text)
    def main(self):
        salt, lt, execution =  self.get_salt()
        sign = self.verify_capcha()
        self.login(salt, lt, execution, sign)



if '__main__' == __name__:
    auth = IdasUESTC('your_id', 'password')
    auth.main()