#/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import httplib  # Python 2
except ImportError:
    import http.client as httplib  # Python 3
try:
    from urllib import urlencode, quote  # Python 2
except ImportError:
    from urllib.parse import urlencode  # Python 3
import json
import md5
import random
from flask.ext.babel import gettext
from config import BAIDU_APPID, BAIDU_SECRETKEY



def baidu_translate(text, sourceLange, destLang):
    salt = random.randint(32768, 65536)
    myurl = '/api/trans/vip/translate'
    if BAIDU_APPID == "" or BAIDU_SECRETKEY =="":
        return gettext('ERROR: translation service not configured.')
    try:
        sign = BAIDU_APPID+text.encode("utf-8")+str(salt)+BAIDU_SECRETKEY
        m1 = md5.new()
        m1.update(sign)
        sign = m1.hexdigest()
        myurl = myurl+'?appid='+BAIDU_APPID+'&q='+quote(text.encode("utf-8"))+'&from='+sourceLange+'&to='+destLang+'&salt='+str(salt)+'&sign='+sign
        httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = json.loads(httpClient.getresponse().read().decode('utf-8'))
        return response['trans_result'][0]['dst']
    except Exception, e:
         return gettext('Error: Unexpected error.')
