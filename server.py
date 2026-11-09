from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import socket
import storage
from fixtures import sample
from imports import import_csv,export_csv,export_result_csv
from planner import compare,validate,VERSION

ROOT=Path(__file__).resolve().parent
FILES={'/':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def setup(self):
        super().setup();self.connection.settimeout(10)

    def respond(self,status,data,mime='application/json'):
        body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode('utf-8') if mime=='application/json' else data
        self.send_response(status)
        self.send_header('Content-Type',mime+'; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers();self.wfile.write(body)

    def permitted(self,write=False):
        port=self.server.server_address[1]
        hosts={f'127.0.0.1:{port}',f'localhost:{port}'}
        if self.headers.get('Host') not in hosts:
            self.respond(403,{'error':'Nepovolený hostitel.'});return False
        origin=self.headers.get('Origin')
        if write and origin and origin not in {f'http://{h}' for h in hosts}:
            self.respond(403,{'error':'Nepovolený původ požadavku.'});return False
        return True

    def do_GET(self):
        if not self.permitted():return
        path=urlsplit(self.path).path
        if path in FILES:
            name,mime=FILES[path];return self.respond(200,(ROOT/'web'/name).read_bytes(),mime)
        if path=='/api/sample':return self.respond(200,sample())
        if path=='/api/scenarios':return self.respond(200,{'scenarios':storage.list_scenarios(self.server.database)})
        match=re.fullmatch(r'/api/scenarios/([a-f0-9-]{36})',path)
        if match:
            result=storage.load(self.server.database,match.group(1))
            return self.respond(200,result) if result else self.respond(404,{'error':'Scénář neexistuje.'})
        self.respond(404,{'error':'Nenalezeno.'})

    def do_POST(self):
        if not self.permitted(True):return
        try:
            if self.headers.get('Transfer-Encoding') or not self.headers.get('Content-Type','').startswith('application/json'):
                return self.respond(415,{'error':'Očekávám JSON s Content-Length.'})
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=128000:return self.respond(413,{'error':'Limit požadavku je 128 kB.'})
            raw=self.rfile.read(length)
            if len(raw)!=length:raise ValueError('Neúplný požadavek.')
            body=json.loads(raw.decode('utf-8'),parse_constant=lambda value:(_ for _ in ()).throw(ValueError('Neplatné číslo JSON.')))
            if not isinstance(body,dict):raise ValueError('JSON musí být objekt.')
            path=urlsplit(self.path).path
            if path=='/api/plan':return self.respond(200,compare(body.get('data'),body.get('scenario','baseline')))
            if path=='/api/import':return self.respond(200,import_csv(body.get('csv'),body.get('resources')))
            if path=='/api/export':return self.respond(200,{'csv':export_csv(body.get('data'))})
            if path=='/api/export-result':return self.respond(200,{'csv':export_result_csv(body.get('data'),body.get('scenario','baseline'))})
            if path=='/api/scenarios':return self.respond(201,storage.save(self.server.database,body))
            if path=='/api/restore':return self.respond(200,storage.decode(body))
            self.respond(404,{'error':'Nenalezeno.'})
        except (ValueError,TypeError,KeyError,UnicodeError) as error:
            self.respond(400,{'error':str(error)})
        except (socket.timeout,TimeoutError):
            self.respond(408,{'error':'Čtení požadavku překročilo časový limit.'})
        except Exception:
            self.respond(500,{'error':'Výpočet nebo uložení selhalo. Původní data nebyla změněna.'})

    def do_DELETE(self):
        if not self.permitted(True):return
        match=re.fullmatch(r'/api/scenarios/([a-f0-9-]{36})',urlsplit(self.path).path)
        if not match:return self.respond(404,{'error':'Nenalezeno.'})
        removed=storage.delete(self.server.database,match.group(1));self.respond(200 if removed else 404,{'deleted':removed})


def create_server(port=4195,database=None):
    database=Path(database) if database else ROOT/'data'/'planboard.sqlite'
    storage.init(database)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.daemon_threads=True;server.database=database
    return server


if __name__=='__main__':
    server=create_server();print('PlanBoard: http://127.0.0.1:4195',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
