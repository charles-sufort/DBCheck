import sys
import os, re
import io
from contextlib import redirect_stdout
from time import time

def gen_schedules(n):
    S_i = []
    for i in range(4):
        s_i = []
        for j in range(4):
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
    T += " SPEC AG((p2.state[1] = \"W\")-> ( ( !EF p1.state[1] = \"W\" )))\n"
    T += " SPEC AG((p2.state[2] = \"W\")-> ( ( !EF p1.state[1] = \"W\" )))\n"
    T += " SPEC AG((p2.state[1] = \"W\")-> ( ( !EF p1.state[1] = \"R\" )))\n"
    T += " SPEC AG((p2.state[2] = \"W\")-> ( ( !EF p1.state[1] = \"R\" )))\n"
    T += " SPEC AG((p2.state[1] = \"R\")-> ( ( !EF p1.state[1] = \"W\" )))\n"
    T += " SPEC AG((p2.state[2] = \"R\")-> ( ( !EF p1.state[1] = \"W\" )))\n"
    return T

def get_base(n,t):
    base_file = "db_p2_op{}_{}_base.smv".format(n,t)
    base_text = ""  
    with open(base_file,"r") as fo:
        base_text += fo.read()
    base_text += "\n"
    return base_text

def test_smv(Si, base_text,i,n,k,model):
    text = base_text
    text += gen_schedule_smv(Si,model)
    smv_file = "db_p2_op{}_{}_{}_{}.smv".format(k,model,i,n)
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
        R[s] += 1
    print("iteration {} / {}".format(i+1,n))
    for s in R:
        print("spec {}: {}/{}".format(s,R[s],i+1 ))
        

if __name__ == "__main__":
#    n = sys.argv[1]
#    t = sys.argv[2]
#    base_file = "db_p2_op{}_{}_base.smv".format(n,t)  
    k = 6
    model = "sched"
    base_text = get_base(k,model)
    S = gen_schedules(k)
    print(len(S))
    R = {}
    #for i in range(len(S)):
    i = 0
    start = time()
    R_0 = test_smv(S[0],base_text,i,len(S),k,model)
    finish = time()
    print("{} : {}".format(S[0],finish-start))
    mn = len(S)*(finish - start)/(60)
    hr = mn/60
    print(mn)
    print(hr)
    for s in R_0[0]:
        R[s] = 1
    for s in R_0[1]:
        R[s] = 0
#       for i in range(1,len(S)):
#           R_i = test_smv(S[i],base_text,i,len(S),k,model)
#           results_update(R,R_i,i,len(S))

 
