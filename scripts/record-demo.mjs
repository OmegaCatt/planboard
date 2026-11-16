import {record,pythonServer} from './recording.mjs';import {fileURLToPath} from 'node:url';import path from 'node:path';import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../',import.meta.url));
await record({root,slug:'planboard',start:temp=>pythonServer(root,temp,'PLANBOARD_PYTHON','import sys;from server import create_server;s=create_server(0,sys.argv[1]);print("http://127.0.0.1:"+str(s.server_address[1]),flush=True);s.serve_forever()',[path.join(temp,'history.sqlite')]),walk:async({p,cue,hold,ui})=>{
  await p.waitForFunction(()=>!document.querySelector('#result').hidden&&!document.querySelector('#run').disabled);
  const late=async()=>await p.locator('#metrics tr').nth(3).locator('td').last().innerText();assert.equal(await late(),'6');
  await cue('Deset připravených zakázek a omezená pracoviště. Základní plán má šest pozdních zakázek.');await p.locator('#metrics').scrollIntoViewIfNeeded();await hold(4);
  await cue('Přidáme paralelní kapacitu pracoviště.');await hold(1.2);await ui.select(p.locator('#scenario'), 'capacity');await p.waitForFunction(()=>!document.querySelector('#result').hidden&&!document.querySelector('#run').disabled);assert.equal(await late(),'0');
  await cue('Přidání paralelní kapacity v tomto příkladu odstraní zpoždění. Výsledek se právě vypočítal.');await p.locator('#metrics').scrollIntoViewIfNeeded();await hold(4);
  await cue('Klikneme na operaci v časovém plánu.');await hold(1.2);await ui.click(p.locator('.operation').first());await p.locator('#detail-dialog').waitFor({state:'visible'});
  await cue('Detail operace vysvětluje návaznosti a čekání. Plán ověřuje samostatný kontrolor.');await hold(4);await ui.click(p.locator('[data-close="detail-dialog"]'));
  await cue('Snížíme denní kapacitu na 30 minut a přepočítáme základní scénář.');await ui.fill(p.locator('#resources input').first(), '30');await ui.select(p.locator('#scenario'), 'baseline');await p.waitForFunction(()=>!document.querySelector('#result').hidden&&!document.querySelector('#run').disabled);assert.equal(await p.locator('#unplanned-note').isVisible(),true);
  await cue('Při příliš malé kapacitě zůstávají nezařazené zakázky viditelné. Jejich vynechání není úspěšnější plán.');await p.locator('#unplanned-note').scrollIntoViewIfNeeded();await hold(5);
  return {jobs:10,baselineLate:6,parallelCapacityLate:0,unscheduledWarningVisible:true};
}});
