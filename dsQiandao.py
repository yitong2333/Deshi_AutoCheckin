import requests
import os
import asyncio
import json
import re
import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# 加载环境变量
load_dotenv()
user = ''
password = ''
userKey = ''
practiceKey = ''
cookies = ''
name = ''
entity_key = ''
scope_key = ''
location = ''
# 获取cookies
async def getCookies():
    global cookies,userKey,name
    url = "http://103.239.153.192:8081/suite/appLogin/login.do"

    payload = f'loginName={user}&password={password}%3D&_eZioSuite2022=5.0'
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '65',
    'Host': '103.239.153.192:8081',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
    }
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = requests.request("POST", url, headers=headers, data=payload)
    # 获取返回值
    errorMsg = json.loads(response.text)
    if errorMsg['success']:
        # 获取ck成功事件
        cookies = response.headers.get('Set-Cookie').split(';')[0]
        print('['+time+'] '+'获取cookies成功 Cookies:'+cookies)
        name = errorMsg['data']['userName']
        userKey = errorMsg['data']['userKey']
        print('['+time+'] '+'登录成功！')
        print('['+time+'] '+'当前用户:'+name)
        print('['+time+'] '+'用户key:'+userKey)
        print('['+time+'] '+'开始获取PracticeKey')
        await getPracticeKey()
    else:
        # 获取失败的原因
        print('['+time+'] '+ errorMsg['message'])

# 获取PracticeKey
async def getPracticeKey():
    global practiceKey
    url = "http://103.239.153.192:8081/suite/weChatPublic/weChatView.do?feature=weChat&action=myApplication"
    payload = {}
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Cookie': cookies,
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://103.239.153.192:8081/suite/androidHippo/practiceInfo.do?userKey=69076014',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    a_tag = soup.find("a")
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有带有 href 属性的 <a> 标签
    a_tags = soup.find_all('a', href=True)

    # 初始化一个变量用于存储第一个找到的 practiceKey
    practice_key = None

    # 遍历所有 <a> 标签，提取第一个 practiceKey 的值
    for a_tag in a_tags:
        href = a_tag['href']
        query_params = parse_qs(urlparse(href).query)
        practice_key = query_params.get('practiceKey')
        if practice_key:
            practice_key = practice_key[0]  # 获取第一个 practiceKey 的值
            break  # 找到第一个后立即停止搜索

    # 打印提取到的 practiceKey 值
    if practice_key:
        practiceKey = practice_key
        print(f'['+time+'] '+'Found practiceKey:'+practiceKey)
        #print('['+time+'] '+'开始签到')
        await getSignKey()
    else:
        print('No practiceKey found') 
        
async def getSignKey():
    global practiceKey,userKey,entity_key,scope_key
    url = f"http://103.239.153.192:8081/suite/androidHippo/viewSign.do?userKey={userKey}&practiceKey={practiceKey}&logType=&address="
    payload = {
        "userKey":userKey,
        "practiceKey":practiceKey
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Cookie": cookies,
        "Proxy-Connection": "keep-alive",
        "Referer": "http://103.239.153.192:8081/suite/androidHippo/viewSign.do?userKey={userKey}&practiceKey={practiceKey}&logType=&address=",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "iframe",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    html = response.text
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    soup = BeautifulSoup(html, "lxml")
    entity_key_match = re.search(r"entityKey:\s*['\"](\d+)['\"]", html)
    scope_key_match = re.search(r"scopeKey:\s*['\"](\d+)['\"]", html)
    #print(html)
    if entity_key_match:
        entity_key = entity_key_match.group(1)
        print(f'['+time+'] '+"Extracted entityKey:"+entity_key)
    else:
        print(f'['+time+'] '+"entityKey not found.")

    if scope_key_match:
        scope_key = scope_key_match.group(1)
        print(f'['+time+'] '+'Extracted scope_key:'+ scope_key)
    else:
        print(f'['+time+'] '+"scopeKey not found.")
    # p_tag = soup.find("p", class_="col9")
    # if p_tag == None:
    #     print("cookies过期了")
    # em_tags = p_tag.find_all("em")
    # print(em_tags)
    # numbers = [int(em.text) for em in em_tags]
    # if numbers[0] >= numbers[1]:
    #     print('['+time+'] '+'签到成功！')
    # else:
    #     print('['+time+'] '+'签到失败！')

# 获取并拼接地址
async def getGeo():
    url = "https://h5gw.map.qq.com/ws/location/v1/ip?callback=window._JSONP_callback.JSONP5490&ip=123.232.120.108&key=UTOBZ-2B7R5-MC5IH-QF4IX-A2V45-AAB4V&apptag=h5loc_ip_loc&output=jsonp&t=1724893133069"

    payload = {}
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://apis.map.qq.com/',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    json_data = response.json()
    print(json_data['result']['ad_info']['city'])

    

# 签到
async def sign():
    global practiceKey,userKey,entity_key,scope_key,location
    url = "http://103.239.153.192:8081/suite/androidHippo/workSignIn.do"
    payload=f'entityKey={entity_key}&address={location}&userKey={userKey}&scopeKey={scope_key}&scopeType=2&signTag='
    headers = {
    'Proxy-Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': 'SESSION=056a0bf3-e4f9-4186-bccf-11a360f64dad',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if response.text == 'success':
        print('['+time+'] '+'签到成功！')
    else:
        print('['+time+'] '+'签到失败！')
    

# 主函数
async def main():
    global user,password,location
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    location = os.getenv('LOCATION')
    print(
    """
##  ##     ####   #### ##   ## ##   ###  ##   ## ##
##  ##      ##    # ## ##  ##   ##    ## ##  ##   ##
##  ##      ##      ##     ##   ##   # ## #  ##
 ## ##      ##      ##     ##   ##   ## ##   ##  ###
  ##        ##      ##     ##   ##   ##  ##  ##   ##
  ##        ##      ##     ##   ##   ##  ##  ##   ##
  ##       ####    ####     ## ##   ###  ##   ## ##
    """
    )
    await asyncio.sleep(3)
    await getCookies()
    await asyncio.sleep(3)
    await sign()
    
# 运行主协程
asyncio.run(main())