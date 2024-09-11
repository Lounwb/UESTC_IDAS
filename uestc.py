import requests
import re
import execjs
import time
import json
import logging

import utils

requests = requests.Session()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IdasUESTC():
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.base_url = "https://idas.uestc.edu.cn/authserver/"
        self.qrheaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://idas.uestc.edu.cn/',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
        }
        self.cookies = {
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'zh_CN',
            'route': '',
            'JSESSIONID': '',
        }

        self.js = execjs.compile(open('./encrypt.js', 'r', encoding='utf-8').read())
        self.static_file = [
            'custom/css/login.css',
            'custom/css/login1366.css',
            'custom/css/iCheck/custom.css',
            'custom/js/jquery.min.js',
            'custom/images/logo.png',
            'custom/images/bg.png',
            'custom/css/slidercaptcha.css',
            'custom/js/longbow.slidercaptcha.js',
            'custom/js/login-sliderCaptchaCreate.js',
            'custom/images/saoma.png',
            'custom/images/mmdl.png',
            'custom/images/yhdl.png',
            'custom/images/smdl.png',
            'custom/images/remark.png',
            'custom/images/qq.png',
            'custom/images/wx.png',
            'custom/images/dlts.png',
            'custom/images/xjt.png',
            'custom/images/ewm.png',
            'custom/js/login-language.js',
            'custom/js/icheck.min.js',
            'custom/js/login.js',
            'custom/js/login-wisedu_v1.0.js',
            'custom/js/encrypt.js',
            'custom/images/logo.png',
            'custom/images/saoma.png',
            'custom/images/mmdl.png',
            'custom/images/yhdl.png',
            'custom/images/smdl.png',
            'custom/images/remark.png',
            'custom/images/qq.png',
            'custom/images/wx.png',
            'custom/images/dlts.png',
            'custom/images/xjt.png',
            'custom/images/ewm.png',
            'custom/images/icons.png',
        ]
 
    def _get_salt(self):
        url = "https://idas.uestc.edu.cn/authserver/login"
        headers = {
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
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page = response.text
        # salt = re.findall('var pwdDefaultEncryptSalt = "(.*?)";', page)[0]
        salt = re.search(r'var pwdDefaultEncryptSalt = "([^"]+)"', page).group(1)
        lt = re.search(r'name="lt" value="([^"]+)"', page).group(1)
        execution = re.search(r'name="execution" value="([^"]+)"', page).group(1)
        # state = re.search(r'&state=([^"]+)"', page).group(1)

        route = response.cookies.get('route')
        JSESSIONID = response.cookies.get('JSESSIONID')
        
        self.cookies['route'] = route
        self.cookies['JSESSIONID'] = JSESSIONID

        return salt, lt, execution

    def _relogin(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }
        url = "https://idas.uestc.edu.cn/authserver/login"
        requests.get(url, headers=headers, cookies=self.cookies)
        self._get_static_file()

    def _get_static_file(self):
        url = "https://idas.uestc.edu.cn/authserver/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "image/avif,image/webp,*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://idas.uestc.edu.cn/authserver/login",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        for file in self.static_file:
            if file.endswith('.js'):
                headers['Accept'] = '*/*'
                headers['Sec-Fetch-Dest'] = 'script'
            elif file.endswith('.css'):
                headers['Accept'] = 'text/css,*/*;q=0.1'
                headers['Sec-Fetch-Dest'] = 'style'
            elif file.endswith(('.png', '.ico')):
                headers['Accept'] = 'image/avif,image/webp,*/*'
                headers['Sec-Fetch-Dest'] = 'image'
            requests.get(url + file, headers=headers, cookies=self.cookies)

    def _combined_login(self):
        url = "https://idas.uestc.edu.cn/authserver/combinedLogin.do"
        params = {
            'type': 'weixin',
            'success': 'https://idas.uestc.edu.cn/authserver/login'
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://idas.uestc.edu.cn/authserver/login",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin"
        }


        response = requests.get(url, params=params, cookies=self.cookies, headers=headers)
        state = re.search(r'&state=([^"]+)"', response.text).group(1)
        return state
    
    def _qrconnect_f(self):
        state = self._combined_login()
        url = "https://open.weixin.qq.com/connect/qrconnect"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://idas.uestc.edu.cn/",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }
        params = {
            'appid': 'wxde827ea01ed92af7',
            'redirect_uri': 'https://idas.uestc.edu.cn/authserver/callback',
            'response_type': 'code',
            'scope': 'snsapi_login',
            'state': state
        }

        response = requests.get(url, params=params, headers=self.qrheaders)
        uuid = re.search(r'uuid=([^"]+)"', response.text).group(1)
        url = [
            'https://idas.uestc.edu.cn/favicon.ico',
            'https://res.wx.qq.com/t/wx_fed/weui-source/res/2.5.4/weui.min.css',
            'https://res.wx.qq.com/t/wx_fed/mp/connect/res/static/css/eb891745f5ce5971ec7c64dfb6f37c09.css',
            'https://open.weixin.qq.com/connect/qrcode/061a2l0T1pAUkl2o',
            'https://res.wx.qq.com/t/wx_fed/cdn_libs/res/jquery/1.11.3/jquery.min.js'
        ]
        for u in url:
            if u.startswith('https://idas.uestc.edu.cn'):
                headers['Referer'] = 'https://idas.uestc.edu.cn/authserver/login'
            else:
                headers['Referer'] = 'https://open.weixin.qq.com'
            
            if u.endswith('.js'):
                headers['Accept'] = '*/*'
                headers['Sec-Fetch-Dest'] = 'script'
            elif u.endswith('.css'):
                headers['Accept'] = 'text/css,*/*;q=0.1'
                headers['Sec-Fetch-Dest'] = 'style'
            elif u.endswith(('.png', '.ico')):
                headers['Accept'] = 'image/avif,image/webp,*/*'
                headers['Sec-Fetch-Dest'] = 'image'

            requests.get(u, headers=self.qrheaders, cookies=self.cookies)
        return uuid

    def _qrconnect_s(self, uuid):
        timestamp = int(time.time())
        url = 'https://lp.open.weixin.qq.com/connect/l/qrconnect'
        params = {
            'uuid': uuid,
            '_': timestamp 
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://open.weixin.qq.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site"
        }
        response = requests.get(url, params=params, headers=headers)


    def _need_capcha(self):
        url = "https://idas.uestc.edu.cn/authserver/needCaptcha.html"
        timestamp = int(time.time())
        params = {
            'username': self.username,
            'pwdEncrypt2': 'pwdEncryptSalt',
            '_': timestamp
        }
        response = requests.get(url, params=params, cookies=self.cookies)
        print(response.text)
        return response.text

    def _get_capcha(self):
        need_capcha = self._need_capcha()
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
    def _verify_capcha(self):
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
            moveLength = self._get_capcha()
            response = get_verify(moveLength)
            data = json.loads(response)
            code = data['code']
        sign = data['sign']
        return sign

    def _login(self, salt, lt, execution, sign):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://idas.uestc.edu.cn",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://idas.uestc.edu.cn/authserver/login",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        params = {
            'service': 'https://eportal.uestc.edu.cn/login?service=https://eportal.uestc.edu.cn/new/index.html?browser=no',
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
        response = requests.post(url, headers=headers, data=data, params=params)
        print(response.text)

    def main(self):
        # get_salt -> staticfile(normal) -> relogin -> staticfile(abnormal) -> combinedlogin -> qrconnect -> verify_capcha -> login
        salt, lt, execution = self._get_salt()
        sign = self._verify_capcha()
        self._login(salt, lt, execution, sign)
        # uuid = self._qrconnect_f()
        # self._qrconnect_s(uuid)
        # sign = self._verify_capcha()
        # self._login(salt, lt, execution, sign)



if '__main__' == __name__:
    auth = IdasUESTC('2021090921009', 'litianyu2002')
    auth.main()