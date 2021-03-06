import http.client
import json
import os
from time import sleep


class Downloader:

    def __init__(self, rapidapi_config, api, data_dir="./data", overwrite=False, delay=0):
        self.rapidapi_host = rapidapi_config['host']
        self.rapidapi_key = rapidapi_config['key']
        self.api_name = api['name']
        self.api_path = api['path']
        self.api_content = False
        if 'content' in api:
            self.api_content = api['content']
        self.data_dir = data_dir
        self.overwrite = overwrite
        self.delay = delay

    def build_path(self, tconst):
        basedir = self.data_dir+'/download/'+self.api_name
        key = format(int(tconst[2:]), '08d')
        # reverse the id to obtain a partitionable key
        tpath = key[6:8]+'/'+key[4:6]+'/'+key[2:4]
        return basedir+'/'+tpath

    def call_api(self, tconst):
        conn = http.client.HTTPSConnection(self.rapidapi_host)
        headers = {
            'x-rapidapi-host': self.rapidapi_host,
            'x-rapidapi-key': self.rapidapi_key
        }
        url = self.api_path.format(tconst)
        print('\t call get on {}'.format(url))
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        resh = res.getheaders()
        # TODO check rapidApi limit header to avoid overquota
        body = res.read()
        data = (body.decode("utf-8"))
        return json.loads(data)

    def write_json(self, tconst, data):
        basedir = self.build_path(tconst)
        if not os.path.exists(basedir):
            print('\t mkdirs {}'.format(basedir))
            os.makedirs(basedir)
        outpath = basedir + '/'+tconst + '.json'
        with open(outpath, 'w') as outfile:
            print('\t write to {}'.format(outpath))
            json.dump(data, outfile)

    def download_title(self, tconst):
        try:
            skip = False
            if not self.overwrite:
                # check if file exists and skip
                outpath = self.build_path(tconst) + '/'+tconst + '.json'
                print('\t check overwrite for {}'.format(outpath))
                skip = os.path.exists(outpath)
            if skip:
                print('\t skip {}: existing'.format(tconst))
            else:
                print('\t download {}'.format(tconst))
                print('\t call api for {} on tconst {}'.format(
                    self.api_name, tconst))
                # check delay
                if(self.delay > 0):
                    sleep(self.delay)
                js = self.call_api(tconst)
                if self.api_content:
                    if not self.api_content in js:
                        print('\t \t debug {}'.format(js))
                        raise Exception(
                            'missing key {} for {}, skip.'.format(self.api_content, tconst))
                print('\t save response for {} on tconst {}'.format(
                    self.api_name, tconst))
                self.write_json(tconst, js)
        except Exception as err:
            print('\t error on {}: {}'.format(tconst, err))
            raise err

    def download(self, titles):
        print('\t download api {} on {} titles'.format(
            self.api_name, titles.len()))
        for tconst in titles:
            try:
                self.download_title(tconst)
                print('\t done {}'.format(tconst))
            except Exception as err:
                print('\t skip {} for error: {}'.format(tconst, err))
