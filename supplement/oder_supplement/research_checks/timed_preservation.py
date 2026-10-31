"""Exact finite timed-query checks; direct grouped policies versus trajectory covers."""
from itertools import product, combinations
import json
X=list(product((0,1),repeat=2))
D=60

def feature(x,mask):return tuple(X[x][j] for j in range(2) if mask>>j&1)
def terminal_choices(target,t):
    return ({('act',target)} if t+20<=D else set()) | ({('both',)} if t+50<=D else set())
def advance(x,op,t,routes,targets,durations,keep):
    if op[0]=='query':
        if op[1]!='slow' and op[1]!=routes[x]:return None
        dt=durations[1] if op[1]=='slow' else durations[0]
        return ('ready',t+dt,targets[x] if keep else 0)
    return None
OPS=[('act',0),('act',1),('both',),('query',0),('query',1),('query','slow')]

def witnesses(t,routes,targets,durations,keep):
    opts=[]
    for x in range(4):
        local=[]
        for op in OPS:
            if op[0]!='query':
                if op in terminal_choices(targets[x],t):local.append(((('start',t),op),))
            else:
                r=advance(x,op,t,routes,targets,durations,keep)
                if r:
                    for act in terminal_choices(targets[x],r[1]):local.append(((('start',t),op),(r,act)))
        opts.append(local)
    return product(*opts)

def covered(w,mask):
    entries=[(x,r,op) for x,steps in enumerate(w) for r,op in steps]
    return all(r!=s or op==a or feature(x,mask)!=feature(y,mask) for (x,r,op),(y,s,a) in combinations(entries,2))

def direct(t,routes,targets,durations,keep,mask):
    groups={}
    for x in range(4):groups.setdefault(feature(x,mask),[]).append(x)
    alternatives=[]
    for xs in groups.values():
        candidates=[]
        for op in OPS:
            stopping=[];valid=True
            for x in xs:
                if op[0]!='query':
                    if op not in terminal_choices(targets[x],t):valid=False;break
                else:
                    r=advance(x,op,t,routes,targets,durations,keep)
                    if r is None:valid=False;break
                    stopping.append((x,r))
            if valid:candidates.append(stopping)
        if not candidates:return False
        alternatives.append(candidates)
    for profile in product(*alternatives):
        allowed={};valid=True
        for part in profile:
            for x,r in part:
                key=(r,feature(x,mask));choices=terminal_choices(targets[x],r[1])
                allowed[key]=allowed.get(key,choices)&choices
                if not allowed[key]:valid=False;break
            if not valid:break
        if valid:return True
    return False

def check():
    comparisons=0
    for targets in product((0,1),repeat=4):
        for routes in [(0,0,1,1),(0,1,0,1),(0,0,0,0),(0,1,1,0)]:
            for keep in [False,True]:
                for durations in [(5,25),(10,20),(0,0)]:
                    for t in [5,15,25,35,40,41]:
                        ws=list(witnesses(t,routes,targets,durations,keep))
                        for mask in range(4):
                            a=direct(t,routes,targets,durations,keep,mask)
                            b=any(covered(w,mask) for w in ws)
                            assert a==b,(targets,routes,keep,durations,t,mask)
                            comparisons+=1
    routes=(0,0,1,1);targets=(0,1,0,1);durations=(5,25)
    rows=[]
    for t in range(61):
        feasible=[m for m in range(4) if direct(t,routes,targets,durations,True,m)]
        costs={0:0,1:1,2:2,3:3}
        rows.append((t,min((costs[m] for m in feasible),default=None)))
    assert rows[15][1]==0 and rows[16][1]==1 and rows[35][1]==1 and rows[36][1]==2 and rows[40][1]==2 and rows[41][1] is None
    assert not direct(30,routes,targets,durations,False,1)
    return {'temporal_policy_cover_comparisons':comparisons,'disagreements':0,'minimum_cost_intervals':{'0..15':0,'16..35':1,'36..40':2,'41..60':None},'locator_independent_of_target':True,'locator_success_at_30_with_reply_retained':True,'locator_success_at_30_with_reply_overwritten':False,'deadline':60,'targeted_duration':20,'fast_query_duration':5,'generic_query_duration':25,'common_action_duration':50}
