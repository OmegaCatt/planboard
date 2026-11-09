import unittest
import random
from copy import deepcopy
from planner import schedule,compare,verify,validate
from fixtures import sample
from imports import export_csv,import_csv

def simple(jobs,resources=None):
    return {'resources':resources or [{'id':'a','name':'Pracoviště A','capability':'a','dailyMinutes':480,'blackouts':[]}],'jobs':jobs}

def job(key,minutes,day=1,priority=0):
    return {'id':key,'customer':'Fiktivní zákazník','dueDay':day,'priority':priority,'operations':[{'machine':'a','minutes':minutes}]}

class PlannerTests(unittest.TestCase):
    def test_small_plan_has_known_completion_and_no_overlap(self):
        data=simple([job('B',100),job('A',100)])
        result=schedule(data)
        self.assertEqual([(o['jobId'],o['start'],o['end']) for o in result['operations']],[('A',0,100),('B',100,200)])
        self.assertEqual(result['metrics'],{'jobs':2,'planned':2,'unplanned':0,'lateJobs':0,'lateMinutes':0})
    def test_priority_is_applied_before_due_date(self):
        result=schedule(simple([job('A',100),job('Z',100,5,1)]))
        self.assertEqual(result['operations'][0]['jobId'],'Z')
    def test_operation_never_crosses_shift_or_predecessor(self):
        item=job('A',300);item['operations'].append({'machine':'a','minutes':300})
        result=schedule(simple([item]));self.assertEqual([(o['start'],o['end']) for o in result['operations']],[(0,300),(480,780)])
        self.assertEqual(result['jobs'][0]['lateMinutes'],300)
    def test_blackout_union_and_capacity_metrics(self):
        resources=[{'id':'a','name':'A','capability':'a','dailyMinutes':480,'blackouts':[[0,100],[50,150]]}]
        result=schedule(simple([job('A',60)],resources));self.assertEqual(result['operations'][0]['start'],150)
        self.assertEqual(result['resources'][0]['availableMinutes'],2250)
        self.assertAlmostEqual(result['resources'][0]['utilization'],60/2250)
    def test_infeasible_job_rolls_back_all_tentative_operations(self):
        resources=[{'id':'a','name':'A','capability':'a','dailyMinutes':480},{'id':'b','name':'B','capability':'b','dailyMinutes':50}]
        impossible=job('A',100);impossible['operations'].append({'machine':'b','minutes':60})
        result=schedule(simple([impossible,job('B',100)],resources))
        self.assertEqual([(o['jobId'],o['start'],o['end']) for o in result['operations']],[('B',0,100)])
        self.assertEqual(result['metrics']['unplanned'],1);self.assertIsNone(result['jobs'][0]['lateMinutes'])
    def test_zero_available_capacity_is_visible(self):
        data=simple([job('A',100)]);data['resources'][0]['blackouts']=[[0,2400]]
        result=schedule(data);self.assertEqual(result['metrics']['unplanned'],1);self.assertIsNone(result['resources'][0]['utilization'])
    def test_demo_scenarios_are_computed_and_input_remains_unchanged(self):
        data=sample();original=deepcopy(data)
        expected={'baseline':(10,6,1800),'outage':(10,6,2790),'urgent':(11,7,2670),'capacity':(10,0,0)}
        for name,values in expected.items():
            result=compare(data,name)
            self.assertEqual(tuple(result['changed']['metrics'][key] for key in ('jobs','lateJobs','lateMinutes')),values)
            self.assertEqual(verify(result['input'],result['changed']),[])
        self.assertEqual(data,original)
    def test_independent_checker_rejects_wrong_metrics_and_schedule(self):
        data=simple([job('A',300),job('B',100)])
        for mutate in [lambda r:r['metrics'].update(lateJobs=99),lambda r:r['operations'][1].update(start=50,end=150),lambda r:r['jobs'][0].update(due=0),lambda r:r['resources'][0].update(usedMinutes=0)]:
            result=schedule(data);mutate(result);self.assertTrue(verify(data,result))
    def test_wait_explanation_matches_real_release_calendar_and_occupancy(self):
        result=schedule(simple([job('A',300),job('B',300)]))
        second=result['operations'][1]
        self.assertEqual(second['release'],0)
        self.assertEqual(second['calendarStart'],0)
        self.assertEqual(second['start'],480)
        self.assertEqual(second['occupancyWait'],480)
        self.assertEqual(second['calendarWait']+second['occupancyWait'],second['start']-second['release'])
    def test_invalid_inputs_are_rejected(self):
        for mutate in [lambda d:d['jobs'].append(deepcopy(d['jobs'][0])),lambda d:d['jobs'][0].update(dueDay=6),lambda d:d['jobs'][0]['operations'][0].update(minutes=True),lambda d:d['resources'][0].update(dailyMinutes=0),lambda d:d['resources'][0].update(blackouts=[[100,50]])]:
            data=simple([job('A',100)]);mutate(data)
            with self.assertRaises(ValueError):validate(data)
    def test_csv_roundtrip_and_formula_safe_customer(self):
        data=sample();self.assertEqual(import_csv(export_csv(data),data['resources']),data)
        data['jobs'][0]['customer']='=HYPERLINK("x")';self.assertIn("'=HYPERLINK",export_csv(data))
        with self.assertRaises(ValueError):import_csv('wrong;columns\n1;2',data['resources'])
    def test_seeded_varied_inputs_are_feasible_or_explicitly_unplanned(self):
        rng=random.Random(73)
        for n in range(30):
            data=simple([job(f'J{i:03}',rng.randint(1,480),rng.randint(1,5),rng.randint(0,1)) for i in range(rng.randint(1,50))])
            data['resources'][0]['dailyMinutes']=rng.randint(30,480)
            result=schedule(data);self.assertEqual(verify(data,result),[]);self.assertEqual(result['metrics']['jobs'],len(data['jobs']))

if __name__=='__main__':unittest.main()
