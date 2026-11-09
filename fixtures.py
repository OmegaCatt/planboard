def sample():
    resources=[{'id':key,'name':name,'capability':key,'dailyMinutes':480,'blackouts':[]} for key,name in [('assembly','Montáž'),('cut','Řezání'),('pack','Balení')]]
    jobs=[]
    for i in range(10):
        route=['cut','assembly'] if i%2==0 else ['assembly','pack']
        jobs.append({'id':f'Z-{i+1:03}','customer':f'Fiktivní zákazník {i+1}','dueDay':1+i//4,'priority':0,'operations':[{'machine':route[0],'minutes':150+(i%3)*30},{'machine':route[1],'minutes':120+(i%2)*30}]})
    return {'resources':resources,'jobs':jobs}
