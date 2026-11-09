"""Deterministic, finite-capacity planning over a fictional workweek."""
from __future__ import annotations
from copy import deepcopy

VERSION = 1
DAY = 480
HORIZON = 5 * DAY


def integer(value, minimum, maximum):
    return type(value) is int and minimum <= value <= maximum


def text(value, limit=80):
    return isinstance(value, str) and 0 < len(value.strip()) <= limit and not any(ord(c) < 32 for c in value)


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Zadání musí být objekt.')
    resources, jobs = data.get('resources'), data.get('jobs')
    if not isinstance(resources, list) or not 1 <= len(resources) <= 8:
        raise ValueError('Zadejte 1 až 8 pracovišť.')
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 200:
        raise ValueError('Zadejte 1 až 200 zakázek.')
    resource_ids, capabilities, job_ids = set(), set(), set()
    for r in resources:
        if not isinstance(r, dict) or not all(text(r.get(k)) for k in ('id', 'name', 'capability')) or r['id'] in resource_ids:
            raise ValueError('Pracoviště musí mít jedinečné ID, název a typ operace.')
        resource_ids.add(r['id'])
        capabilities.add(r['capability'])
        if not integer(r.get('dailyMinutes'), 1, DAY):
            raise ValueError('Denní kapacita musí být 1 až 480 minut.')
        blocks = r.get('blackouts', [])
        if not isinstance(blocks, list) or len(blocks) > 20:
            raise ValueError('Příliš mnoho výpadků pracoviště.')
        for block in blocks:
            if not isinstance(block, list) or len(block) != 2 or not all(integer(v, 0, HORIZON) for v in block) or block[0] >= block[1]:
                raise ValueError('Neplatný interval výpadku.')
    for j in jobs:
        if not isinstance(j, dict) or not text(j.get('id')) or j['id'] in job_ids or not text(j.get('customer')):
            raise ValueError('Zakázka musí mít jedinečné ID a zákazníka.')
        job_ids.add(j['id'])
        if not integer(j.get('dueDay'), 1, 5) or not integer(j.get('priority', 0), 0, 1):
            raise ValueError('Termín musí být pracovní den 1–5 a priorita 0/1.')
        operations = j.get('operations')
        if not isinstance(operations, list) or not 1 <= len(operations) <= 2:
            raise ValueError('Zakázka musí mít 1 až 2 navazující operace.')
        for op in operations:
            if not isinstance(op, dict) or op.get('machine') not in capabilities or not integer(op.get('minutes'), 1, DAY):
                raise ValueError('Operace vyžaduje známý typ pracoviště a délku 1–480 minut.')
    return deepcopy(data)


def availability(resource):
    """Subtract the union of blackouts from each separate working shift."""
    segments = []
    for day in range(5):
        current = [(day * DAY, day * DAY + resource['dailyMinutes'])]
        for left, right in sorted(resource.get('blackouts', [])):
            remaining = []
            for start, end in current:
                if right <= start or left >= end:
                    remaining.append((start, end))
                else:
                    if start < left:
                        remaining.append((start, left))
                    if right < end:
                        remaining.append((right, end))
            current = remaining
        segments.extend(current)
    return segments


def find_slot(windows, occupied, release, duration):
    for left, right in windows:
        start = max(left, release)
        for busy_start, busy_end in sorted(occupied):
            if busy_end <= start:
                continue
            if busy_start >= start + duration:
                break
            start = busy_end
        if start + duration <= right:
            return start
    return None


def schedule(data):
    data = validate(data)
    resources = data['resources']
    windows = {r['id']: availability(r) for r in resources}
    occupied = {r['id']: [] for r in resources}
    operations, outcomes = [], []
    for job in sorted(data['jobs'], key=lambda j: (-j.get('priority', 0), j['dueDay'], j['id'])):
        pending, release, failure = [], 0, None
        for index, op in enumerate(job['operations']):
            candidates = []
            for resource in resources:
                if resource['capability'] != op['machine']:
                    continue
                local = occupied[resource['id']] + [(p['start'], p['end']) for p in pending if p['resource'] == resource['id']]
                start = find_slot(windows[resource['id']], local, release, op['minutes'])
                if start is not None:
                    candidates.append((start, resource['id']))
            if not candidates:
                failure = f"Pro zvolené pořadí se operace {index + 1} ({op['machine']}, {op['minutes']} min) po dokončení předchůdce nevejde do dostupných směn pětidenního horizontu. Jiné pořadí může dát jiný výsledek."
                break
            start, resource_id = min(candidates)
            calendar_start=find_slot(windows[resource_id],[],release,op['minutes'])
            pending.append({'jobId': job['id'], 'operation': index + 1, 'resource': resource_id, 'start': start, 'end': start + op['minutes'], 'release':release, 'calendarStart':calendar_start, 'calendarWait':calendar_start-release, 'occupancyWait':start-calendar_start})
            release = start + op['minutes']
        if failure:
            outcomes.append({'id': job['id'], 'customer': job['customer'], 'due': job['dueDay'] * DAY, 'status': 'unplanned', 'completion': None, 'lateMinutes': None, 'reason': failure})
            continue  # Atomic planning: no abandoned operation consumes capacity.
        operations.extend(pending)
        for item in pending:
            occupied[item['resource']].append((item['start'], item['end']))
        late = max(0, release - job['dueDay'] * DAY)
        outcomes.append({'id': job['id'], 'customer': job['customer'], 'due': job['dueDay'] * DAY, 'status': 'late' if late else 'onTime', 'completion': release, 'lateMinutes': late, 'reason': 'Priorita, termín, návaznosti a nejbližší dostupný interval; heuristika bez záruky optimálního plánu.'})
    outcomes.sort(key=lambda j: j['id'])
    result = {'version': VERSION, 'operations': operations, 'jobs': outcomes, 'resources': []}
    for resource in resources:
        available = sum(end - start for start, end in windows[resource['id']])
        used = sum(end - start for start, end in occupied[resource['id']])
        result['resources'].append({'id': resource['id'], 'name': resource['name'], 'availableMinutes': available, 'usedMinutes': used, 'utilization': used / available if available else None})
    result['metrics'] = {'jobs': len(outcomes), 'planned': sum(j['status'] != 'unplanned' for j in outcomes), 'unplanned': sum(j['status'] == 'unplanned' for j in outcomes), 'lateJobs': sum(j['status'] == 'late' for j in outcomes), 'lateMinutes': sum(j['lateMinutes'] or 0 for j in outcomes)}
    errors = verify(data, result)
    if errors:
        raise RuntimeError('Kontrola plánu selhala: ' + '; '.join(errors))
    return result


def verify(data, result):
    """Independent result checker. Does not call scheduling or find_slot."""
    errors = []
    resources = {r['id']: r for r in data['resources']}
    jobs = {j['id']: j for j in data['jobs']}
    by_job, by_resource = {}, {}
    for item in result['operations']:
        job = jobs.get(item['jobId'])
        resource = resources.get(item['resource'])
        if not job or not resource or not integer(item['operation'], 1, len(job['operations'])):
            errors.append('Neznámá operace nebo pracoviště')
            continue
        spec = job['operations'][item['operation'] - 1]
        start, end = item['start'], item['end']
        if not integer(start, 0, HORIZON) or not integer(end, 1, HORIZON) or end - start != spec['minutes'] or resource['capability'] != spec['machine']:
            errors.append('Délka nebo kompatibilita operace')
        elif start // DAY != (end - 1) // DAY or end > start // DAY * DAY + resource['dailyMinutes']:
            errors.append('Operace mimo směnu')
        if any(start < right and end > left for left, right in resource.get('blackouts', [])):
            errors.append('Operace zasahuje do výpadku')
        by_job.setdefault(item['jobId'], []).append(item)
        by_resource.setdefault(item['resource'], []).append(item)
    for rows in by_resource.values():
        rows = sorted(rows, key=lambda o: o['start'])
        if any(a['end'] > b['start'] for a, b in zip(rows, rows[1:])):
            errors.append('Překryv na pracovišti')
    if len(result['jobs']) != len(jobs) or {j['id'] for j in result['jobs']} != set(jobs):
        errors.append('Chybějící nebo duplicitní zakázky')
    for outcome in result['jobs']:
        if outcome['id'] not in jobs:
            errors.append('Neznámá zakázka ve výsledku')
            continue
        if outcome['due']!=jobs[outcome['id']]['dueDay']*DAY:
            errors.append('Nesprávný požadovaný termín')
        rows = sorted(by_job.get(outcome['id'], []), key=lambda o: o['operation'])
        if outcome['status'] == 'unplanned':
            if rows or outcome['completion'] is not None or outcome['lateMinutes'] is not None:
                errors.append('Neplánovaná zakázka spotřebovává kapacitu')
        elif not rows or len(rows) != len(jobs[outcome['id']]['operations']) or [r['operation'] for r in rows] != list(range(1, len(rows) + 1)) or any(a['end'] > b['start'] for a, b in zip(rows, rows[1:])):
            errors.append('Neúplná nebo nenavazující zakázka')
        elif outcome['completion'] != rows[-1]['end'] or outcome['lateMinutes'] != max(0, rows[-1]['end'] - jobs[outcome['id']]['dueDay'] * DAY):
            errors.append('Nesprávný termín nebo zpoždění')
        elif outcome['status'] != ('late' if outcome['lateMinutes'] else 'onTime'):
            errors.append('Nesprávný stav zakázky')
        for index,item in enumerate(rows):
            release=rows[index-1]['end'] if index else 0
            resource=resources[item['resource']]
            duration=item['end']-item['start']
            candidate=item.get('calendarStart')
            def fits(t):
                end=t+duration
                return end<=HORIZON and t//DAY==(end-1)//DAY and end<=t//DAY*DAY+resource['dailyMinutes'] and not any(t<b and end>a for a,b in resource.get('blackouts',[]))
            if item.get('release')!=release or not integer(candidate,release,HORIZON) or candidate>item['start'] or not fits(candidate) or any(fits(t) for t in range(release,candidate)) or item.get('calendarWait')!=candidate-release or item.get('occupancyWait')!=item['start']-candidate:
                errors.append('Nesprávné vysvětlení čekání operace')
    expected={'jobs':len(jobs),'planned':sum(j['status']!='unplanned' for j in result['jobs']),'unplanned':sum(j['status']=='unplanned' for j in result['jobs']),'lateJobs':sum(j['status']=='late' for j in result['jobs']),'lateMinutes':sum(j['lateMinutes'] or 0 for j in result['jobs'])}
    if result['metrics'] != expected:
        errors.append('Nesprávné souhrnné metriky')
    if len(result['resources'])!=len(resources) or {r['id'] for r in result['resources']}!=set(resources):
        errors.append('Chybějící pracoviště v metrikách')
    for item in result['resources']:
        resource=resources.get(item['id'])
        if not resource:
            errors.append('Neznámé pracoviště v metrikách')
            continue
        available=sum(1 for t in range(HORIZON) if t%DAY<resource['dailyMinutes'] and not any(a<=t<b for a,b in resource.get('blackouts',[])))
        used=sum(o['end']-o['start'] for o in by_resource.get(item['id'],[]))
        if item['availableMinutes']!=available or item['usedMinutes']!=used or item['utilization']!=(used/available if available else None):
            errors.append('Nesprávné využití kapacity')
    return errors


def scenario(data, kind):
    data = validate(data)
    if kind == 'baseline':
        return data
    if kind == 'outage':
        data['resources'][0].setdefault('blackouts', []).append([120, 240])
    elif kind == 'urgent':
        if any(j['id'] == 'URGENT-DEMO' for j in data['jobs']):
            raise ValueError('ID URGENT-DEMO je vyhrazeno ukázkovému scénáři.')
        data['jobs'].append({'id': 'URGENT-DEMO', 'customer': 'Fiktivní urgentní zákazník', 'dueDay': 1, 'priority': 1, 'operations': [{'machine': data['resources'][0]['capability'], 'minutes': 180}]})
    elif kind == 'capacity':
        source = deepcopy(data['resources'][0])
        source['id'] = 'EXTRA-DEMO'
        source['name'] += ' – paralelní kapacita'
        if any(r['id'] == source['id'] for r in data['resources']):
            raise ValueError('ID EXTRA-DEMO je vyhrazeno ukázkovému scénáři.')
        data['resources'].append(source)
    else:
        raise ValueError('Neznámý scénář.')
    return validate(data)


def compare(data, kind):
    base, changed_input = schedule(data), scenario(data, kind)
    changed = schedule(changed_input)
    before = {j['id']: j for j in base['jobs']}
    changes = []
    for job in changed['jobs']:
        previous = before.get(job['id'])
        delta = job['completion'] - previous['completion'] if previous and job['completion'] is not None and previous['completion'] is not None else None
        changes.append({'id': job['id'], 'beforeStatus': previous['status'] if previous else None, 'afterStatus': job['status'], 'completionDelta': delta})
    return {'baseline': base, 'changed': changed, 'input': changed_input, 'changes': changes}
