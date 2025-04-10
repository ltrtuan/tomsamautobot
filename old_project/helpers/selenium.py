import time
from sys import platform
from selenium import webdriver
from gologin import GoLogin
from gologin import getRandomPort
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

import http.client
import json


class Selenium():
    @staticmethod
    def open():
       
        gl = GoLogin({
         'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MjAzN2UwNTRjOGVhMTY1YWI5MDZhMWEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2MjAzODljMDBhMTVmZDEzYTQzYjUyNzkifQ.skJa7E2DJQQJwP3zrmFdZNWU0u-OxLk1nYPXHd6ax1Q',
         'profile_id': '64aa7d0a62943b7b5041bc8a',
         'writeCookiesFromServer': True,
         'uploadCookiesToServer': True
        })
        
        debugger_address = gl.start()
        
        service = Service()
        chromedriver_autoinstaller.install()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://youtube.com")
        time.sleep(50)
        driver.close()
        gl.stop()
        
    @staticmethod
    def readCookies():
        conn = http.client.HTTPSConnection("api.gologin.com")
        payload = ''
        headers = {
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MjAzN2UwNTRjOGVhMTY1YWI5MDZhMWEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2MjAzODljMDBhMTVmZDEzYTQzYjUyNzkifQ.skJa7E2DJQQJwP3zrmFdZNWU0u-OxLk1nYPXHd6ax1Q',
          'Content-Type': 'application/json'
        }
        conn.request("GET", "/browser/64aa7d0a62943b7b5041bc8a/cookies", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        
    @staticmethod
    def loadCookies():
        conn = http.client.HTTPSConnection("api.gologin.com")
        payload = json.dumps([
          {
            "url": "https://youtube.com/",
            "domain": ".youtube.com",
            "name": "VISITOR_INFO1_LIVE",
            "value": "LN_n0CYIoZc",
            "hostOnly": False,
            "path": "/",
            "secure": True,
            "sameSite": "no_restriction",
            "httpOnly": True,
            "session": False,
            "expirationDate": 1671888186.9191523
          }
        ])
        headers = {
          'Authorization': 'Bearer YOUR_API_TOKEN',
          'Content-Type': 'application/json'
        }
        conn.request("POST", "/browser/YOUR_PROFILE_ID/cookies", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        
    @staticmethod
    def clearCookies():
        conn = http.client.HTTPSConnection("api.gologin.com")
        payload = json.dumps([])
        headers = {
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MjAzN2UwNTRjOGVhMTY1YWI5MDZhMWEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2MjAzODljMDBhMTVmZDEzYTQzYjUyNzkifQ.skJa7E2DJQQJwP3zrmFdZNWU0u-OxLk1nYPXHd6ax1Q',
          'Content-Type': 'application/json'
        }
        conn.request("POST", "/browser/64aa7d0a62943b7b5041bc8a/cookies?cleanCookies=true", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))