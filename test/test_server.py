import json
import csv
import io
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from fixtures import sample
from server import create_server

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.server=create_server(0,Path(self.temp.name)/'test.sqlite')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_address[1]}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def request(self,path,body=None,method=None,headers=None):
        data=json.dumps(body).encode() if body is not None else None
        req=Request(self.base+path,data=data,method=method or ('POST' if data else 'GET'),headers={'Content-Type':'application/json',**(headers or {})})
        try:
            with urlopen(req,timeout=5) as response:return response.status,response.read(),response.headers
        except HTTPError as e:return e.code,e.read(),e.headers
    def test_real_planning_api_and_browser_files(self):
        status,body,headers=self.request('/');self.assertEqual(status,200);self.assertIn(b'PlanBoard',body);self.assertIn('script-src',headers['Content-Security-Policy'])
        status,body,_=self.request('/api/plan',{'data':sample(),'scenario':'capacity'});self.assertEqual(status,200);self.assertEqual(json.loads(body)['changed']['metrics']['lateJobs'],0)
        self.assertEqual(self.request('/server.py')[0],404)
    def test_history_roundtrip_and_delete(self):
        payload={'version':1,'name':'Testovací scénář','data':sample(),'scenario':'urgent'}
        status,body,_=self.request('/api/scenarios',payload);self.assertEqual(status,201);key=json.loads(body)['id']
        self.assertEqual(len(json.loads(self.request('/api/scenarios')[1])['scenarios']),1)
        self.assertEqual(json.loads(self.request('/api/scenarios/'+key)[1]),payload)
        self.assertEqual(self.request('/api/scenarios/'+key,method='DELETE')[0],200)
        self.assertEqual(self.request('/api/scenarios/'+key)[0],404)
    def test_invalid_input_origin_host_and_size(self):
        self.assertEqual(self.request('/api/plan',{'data':sample()},headers={'Origin':'https://invalid.test'})[0],403)
        self.assertEqual(self.request('/api/sample',headers={'Host':'invalid.test'})[0],403)
        self.assertEqual(self.request('/api/plan',{'data':None})[0],400)
        self.assertEqual(self.request('/api/plan',{'x':'x'*129000})[0],413)
        self.assertEqual(self.request('/api/restore',{'version':99})[0],400)

    def test_result_csv_preserves_unplanned_jobs_and_escapes_text(self):
        data=sample();data['resources'][0]['dailyMinutes']=30
        data['jobs'][0]['customer']='=SUM(1,2)'
        status,body,_=self.request('/api/export-result',{'data':data,'scenario':'baseline'})
        self.assertEqual(status,200)
        rows=list(csv.DictReader(io.StringIO(json.loads(body)['csv'].lstrip('\ufeff')),delimiter=';'))
        self.assertEqual(len(rows),len(data['jobs']))
        self.assertTrue(any(row['status']=='unplanned' and row['completion_work_minute']=='' and row['reason'] for row in rows))
        self.assertEqual(rows[0]['customer'],"'=SUM(1,2)")
        self.assertEqual(self.request('/api/export-result',{'data':data,'scenario':'unknown'})[0],400)

if __name__=='__main__':unittest.main()
