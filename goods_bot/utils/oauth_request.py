import requests
from scrapy.utils.project import get_project_settings
import json
import logging
import os
from utils.helpers import JSON

import glob

class OauthRequest:
    clientId = get_project_settings().get('OAUTH_CLIENT_ID')
    clientSecret = get_project_settings().get('OAUTH_CLIENT_SECRET')
    server = get_project_settings().get('OATH_SERVER')
    access_token = get_project_settings().get('ACCESS_TOKEN_URL')
    token_file = get_project_settings().get('ACCESS_TOKEN_FILE')
    log = logging.getLogger(__name__)
    token = ""

    def getToken(self):
        if self.token:
            return self.token

        if os.path.exists(self.token_file):
            with open(self.token_file, 'rt') as f:
                token = JSON.load(f)
                self.token = token['access_token']
                f.close()
                return self.token

        response = requests.post(self.server + self.access_token, data={
            'grant_type': 'client_credentials',
            'client_id': self.clientId,
            'client_secret': self.clientSecret,
            'scope': "*"
            })

        if response.status_code != 200:
            self.log.fatal("Get token failed %s", response.text)
            return ""

        token = response.json()
        self.token = token['access_token']
        with open(self.token_file, 'w') as f:
            JSON.dump(token, f)
            f.close()
        return self.token

    def refreshToken(self):
        pass

    def post(self, url, json_data):
        token = self.getToken()

        if token:
            response = requests.post(url, headers={'Authorization': 'Bearer %s' % token, 'accept': 'application/json'}, json = json_data)

            if response.status_code == 401:
                self.token = ""
                # 删除token文件
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                token = self.getToken()
                if token == "":
                    raise Exception("Get token FAILED")
                response = requests.post(url, headers={'Authorization': 'Bearer %s' % token, 'accept': 'application/json'}, json = json_data)
            return response

        raise Exception("Get token FAILED")
    
    def get(self, method, url, params):
        token = self.getToken()

        if token:
            response = requests.get(url, params=params, headers={'Authorization': 'Bearer %s' % token, 'accept': 'application/json'})
            if response.status_code == 401:
                self.token = ""
                # 删除token文件
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                token = self.getToken()
                if token == "":
                    raise Exception("Get token FAILED")
                response = requests.get(url, params=params, headers={'Authorization': 'Bearer %s' % token, 'accept': 'application/json'})
            return response

        raise Exception("Get token FAILED")


def main():
    data_folder = 'data/TmallHk'
    req = OauthRequest()
    for filename in glob.glob(data_folder + '/*.json'):
        with open(filename, 'rt') as f:
            goods_obj = JSON.load(f)
            f.close()
            url = 'http://192.168.0.100:8000/capi/goods/addOne'
            resp = req.post(url, goods_obj)
            if resp.status_code != 200:
                req.log.error("增加商品失败: %s", resp.text)

if __name__ == '__main__':
    main()


# $response = $guzzle->post('http://your-app.com/oauth/token', [
#     'form_params' => [
#         'grant_type' => 'client_credentials',
#         'client_id' => 'client-id',
#         'client_secret' => 'client-secret',
#         'scope' => 'your-scope',
#     ],
# ]);
