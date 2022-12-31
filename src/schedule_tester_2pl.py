import sys
import os, re, json
import io
from contextlib import redirect_stdout
from time import time
from pprint import pprint

def gen_schedules(n):
    S_i = []
    for i in range(4):
        s_i = []
        for j in range(5):
            if i == j:
                s_i.append(["1"])
            else:
                s_i.append(["0"])
        S_i.append(s_i)
    S_i_old = S_i
    S_i = []
    for s_i in S_i_old:
        for s_j in S_i_old:
            S_i.append(s_i+s_j)
    P_S_old = [[[],[],[],[],[],[],[],[]]]
    P_S = []
    for i in range(n):
        for p_s in P_S_old:
            for s_i in S_i:
                p_s_new = []
                for k in range(8):
                    new_k = p_s[k] + s_i[k]
                    p_s_new.append(new_k)
                P_S.append(p_s_new)
        P_S_old = P_S
        P_S = []

    return P_S_old

def gen_schedule_smv(s,model):
    T = " ASSIGN\n"      
    Vars = ["S1_w[1]","S1_w[2]","S1_r[1]","S1_r[2]",\
            "S2_w[1]","S2_w[2]","S2_r[1]","S2_r[2]"]
    for i in range(8):
        w = ""  
        for wi in s[i]:
            w += str(wi)
        L = "\t{} := 0b_{};\n".format(Vars[i],w)         
        T += L
    if model == "sched":
        T += "    o := 1;\n\n" 

    # Deadlock
    T += " SPEC AF( p1.finished & p2.finished)\n "
    # WW,WR,RW 
    E = [["\"W\"","\"W\""],["\"R\"","\"W\""],["\"W\"","\"R\""]]
    for e in E:
        for i in range(2):
            for j in range(2):
                i_1 = (i%2)+1
                i_2 = ((i+1)%2)+1
                T += " SPEC AG((p{}.state[{}] = {})-> ( ( !EF ((p{}.state[{}] = {}) & (!(p{}.finished)) ))))\n".format(i_1,j+1,e[0],i_2,j+1,e[1],i_1)

    return T

def gen_schedule_smv(s,model):
    T = " ASSIGN\n"      
    Vars = ["S1_w[1]","S1_w[2]","S1_r[1]","S1_r[2]",\
            "S2_w[1]","S2_w[2]","S2_r[1]","S2_r[2]"]
    for i in range(8):
        w = ""  
        for wi in s[i]:
            w += str(wi)
        L = "\t{} := 0b_{};\n".format(Vars[i],w)         
        T += L
    if model == "c2pl":
        T += "    o := 1;\n\n" 
    # Deadlock
    T += " SPEC AF( p1.finished & p2.finished)\n "
    # WW,WR,RW 
    E = [["\"W\"","\"W\""],["\"R\"","\"W\""],["\"W\"","\"R\""]]
    for e in E:
        for i in range(2):
            for j in range(2):
                i_1 = (i%2)+1
                i_2 = ((i+1)%2)+1
                T += " SPEC AG((p{}.state[{}] = {})-> ( ( !EF ((p{}.state[{}] = {}) & (!(p{}.finished)) ))))\n".format(i_1,j+1,e[0],i_2,j+1,e[1],i_1)
    return T



def get_base(n,t):
    base_file = "db_p2_op{}_{}_base.smv".format(n,t)
    base_text = ""  
    with open(base_file,"r") as fo:
        base_text += fo.read()
    base_text += "\n"
    return base_text

def get_smv_base(path):
    base_text = ""
    with open(path,"r") as fo:
        base_text += fo.read()
    base_text += "\n"
    return base_text


def test_smv(Si, base_text,i,n,k,model):
    text = base_text
    text += gen_schedule_smv(Si,model)
    smv_file = "test.smv"
    path = "tmp/{}".format(smv_file)
    with open(path,"w") as fo:
        fo.write(text)
    cmd = "NuSMV {} > tmp/results.out".format(path)

    os.system(cmd)
    results = ""
    with open("tmp/results.out",'r') as fo:
        results = fo.read()
    p = re.compile("specification (.*)[\t ]*is true\n")
    TS = p.findall(results)
    p = re.compile("specification (.*)[\t ]*is false\n")
    FS = p.findall(results)
    return [TS,FS]

def results_update(R,Ri,i,n):
    for s in Ri[0]:
        R[s][0] += 1
    for s in Ri[1]:
        R[s][1].append(i)
    print("iteration {} / {}".format(i+1,n))
    for s in R:
        print("spec {}: {}/{}".format(s,R[s][0],i+1))

def results_save(R,file_name):
    path = "tmp/" + file_name
    with open(path,'w') as fo:
        json.dump(R,fo)
        

if __name__ == "__main__":
    model = sys.argv[1]
    k = int(sys.argv[2])
#    base_file = "db_p2_op{}_{}_base.smv".format(n,t)  
    path = "db_{}_op{}_base.smv".format(model,str(k))
    base_text = get_smv_base(path)
    S = gen_schedules(k)
    print(len(S))
    pprint(S[:4])
    R = {}
    start = time()
    R_0 = test_smv(S[0],base_text,0,len(S),k,model)
    finish = time()
    print("{} : {}".format(S[0],finish-start))
    mn = len(S)*(finish - start)/(60)
    hr = mn/60
    print(mn)
    print(hr)
    for s in R_0[0]:
        R[s] = [1,[]]
    for s in R_0[1]:
        R[s] = [0,[]]
    for i in range(1,len(S)):
        R_i = test_smv(S[i],base_text,i,len(S),k,model)
        results_update(R,R_i,i,len(S))
    R["S"] = S
    path = "db_{}_op{}_base.test".format(model,k)
    results_save(R,"db_c2pl_op4_base.json")

 
