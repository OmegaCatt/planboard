import csv
import io
from planner import validate,compare

FIELDS=['id','customer','due_day','priority','op1_machine','op1_minutes','op2_machine','op2_minutes']


def safe_text(value):
    text=str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def export_result_csv(data,scenario):
    result=compare(data,scenario)
    output=io.StringIO(newline='');writer=csv.writer(output,delimiter=';')
    writer.writerow(['id','customer','due_work_minute','completion_work_minute','late_work_minutes','completion_delta_minutes','status','reason'])
    changes={item['id']:item['completionDelta'] for item in result['changes']}
    for job in result['changed']['jobs']:
        writer.writerow([safe_text(job['id']),safe_text(job['customer']),job['due'],job['completion'],job['lateMinutes'],changes[job['id']],job['status'],safe_text(job['reason'])])
    return '\ufeff'+output.getvalue()


def import_csv(text,resources):
    if not isinstance(text,str) or len(text.encode('utf-8'))>128000 or '\x00' in text:
        raise ValueError('CSV musí mít nejvýše 128 kB.')
    delimiter=';' if ';' in text.split('\n',1)[0] else ','
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')),delimiter=delimiter)
    if reader.fieldnames!=FIELDS:
        raise ValueError('CSV vyžaduje sloupce: '+', '.join(FIELDS))
    jobs=[]
    for line,row in enumerate(reader,start=2):
        if len(jobs)>=200 or None in row or any(v is None for v in row.values()):
            raise ValueError(f'Řádek {line}: neplatná struktura nebo více než 200 zakázek.')
        try:
            operations=[{'machine':row['op1_machine'].strip(),'minutes':int(row['op1_minutes'])}]
            if row['op2_machine'] or row['op2_minutes']:
                operations.append({'machine':row['op2_machine'].strip(),'minutes':int(row['op2_minutes'])})
            jobs.append({'id':row['id'].strip(),'customer':row['customer'].strip(),'dueDay':int(row['due_day']),'priority':int(row['priority']),'operations':operations})
        except ValueError as e:
            raise ValueError(f'Řádek {line}: den, priorita a délky musí být celá čísla.') from e
    return validate({'resources':resources,'jobs':jobs})


def export_csv(data):
    data=validate(data);output=io.StringIO(newline='');writer=csv.writer(output,delimiter=';');writer.writerow(FIELDS)
    for job in data['jobs']:
        first=job['operations'][0];second=job['operations'][1] if len(job['operations'])>1 else None
        writer.writerow([safe_text(job['id']),safe_text(job['customer']),job['dueDay'],job.get('priority',0),safe_text(first['machine']),first['minutes'],safe_text(second['machine']) if second else '',second['minutes'] if second else ''])
    return '\ufeff'+output.getvalue()
