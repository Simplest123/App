import json
import urllib.parse
import urllib.request
import ssl


method = 'POST'
appcode = '59d70c4fe95f4a9daaf7ba20635f2348'
querys = ''
bodys = {}
url = 'https://idenauthen.market.alicloudapi.com/idenAuthentication'

bodys['idNo'] = '''340421190210182345'''
bodys['name'] = '''张三'''
post_data = urllib.parse.urlencode(bodys).encode('utf-8')

request = urllib.request.Request(url, data=post_data)
request.add_header('Authorization', 'APPCODE ' + appcode)
# 根据API的要求，定义相对应的Content-Type
request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')

# 创建SSL上下文，忽略证书验证
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read().decode('utf-8')
    if content:
        data = json.loads(content)
        print(data.get('respMessage'))
except urllib.error.URLError as e:
    print(f"Request failed: {e.reason}")
