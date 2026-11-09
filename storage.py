import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from uuid import uuid4
from planner import validate, text, VERSION


def init(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS scenarios(id TEXT PRIMARY KEY,name TEXT NOT NULL,created_at TEXT NOT NULL,payload TEXT NOT NULL)')
        db.commit()


def decode(payload):
    if not isinstance(payload,dict) or type(payload.get('version')) is not int or payload.get('version')!=VERSION or payload.get('scenario') not in ('baseline','outage','urgent','capacity') or not text(payload.get('name')):
        raise ValueError('Neplatný nebo nepodporovaný uložený scénář.')
    return {'version':VERSION,'name':payload['name'].strip(),'scenario':payload['scenario'],'data':validate(payload.get('data'))}


def save(path,payload):
    payload=decode(payload)
    key=str(uuid4());created=datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(path)) as db:
        with db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT COUNT(*) FROM scenarios').fetchone()[0]>=100:
                raise ValueError('Místní úložiště má limit 100 scénářů. Odstraňte nepotřebné položky.')
            db.execute('INSERT INTO scenarios VALUES (?,?,?,?)',(key,payload['name'],created,json.dumps(payload,ensure_ascii=False)))
    return {'id':key,'name':payload['name'],'createdAt':created}


def list_scenarios(path):
    with closing(sqlite3.connect(path)) as db:
        return [{'id':r[0],'name':r[1],'createdAt':r[2]} for r in db.execute('SELECT id,name,created_at FROM scenarios ORDER BY created_at DESC')]


def load(path,key):
    with closing(sqlite3.connect(path)) as db:
        row=db.execute('SELECT payload FROM scenarios WHERE id=?',(key,)).fetchone()
    return decode(json.loads(row[0])) if row else None


def delete(path,key):
    with closing(sqlite3.connect(path)) as db:
        with db:
            return db.execute('DELETE FROM scenarios WHERE id=?',(key,)).rowcount>0
