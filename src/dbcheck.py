import sys
import os, re, json
import io
from contextlib import redirect_stdout
from time import time
from pprint import pprint

def gen_schedules1(n):
    S_i = []
    for i in range(4):
        s_i = []
        for j in range(5):
            if i == j:
                s_i.append(["1"])
            else:
                s_i.append(["0"])
        S_i.append(s_i)
    return S_i


def gen_schedules2(n):
    S_i = []
    for i in range(4):
        s_i = []
        for j in range(4):
            if i == j:
                s_i.append(["1"])
            else:
                s_i.append(["0"])
        S_i.append(s_i)
    return S_i



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
    return T

def gen_specs_smv(model):
    # Deadlock
    T = ""
    T += " SPEC AF( p1.finished & p2.finished)\n "
    if model == "naive" or model == "sched":
        T += " LTLSPEC G(((acell.lock = 1 ) & (X (acell.lock = 0 ))) -> X ( G (acell.lock != 1  )))"
    elif model == "2pl" or model == "c2pl":
        T += " LTLSPEC G(((acell.lock = \"1\" | acell.lock = \"1s\" | acell.lock = \"12s\") & (X (acell.lock = \"0\" | acell.lock = \"2s\"))) -> X ( G ((acell.lock != \"1\") & (acell.lock != \"1s\") & (acell.lock != \"12s\"))))"

    # WW,WR,RW 

    E = [["\"W\"","\"W\""],["\"R\"","\"W\""],["\"W\"","\"R\""]]
    for e in E:
        T += " SPEC AG((p1.state[1] = {})-> ( ( !EF ((p2.state[1] = {}) & (!(p1.finished)) ))))\n".format(e[0],e[1])

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
    text += gen_specs_smv(model)
    smv_file = "test.smv"
    path = "tmp/{}".format(smv_file)
    with open(path,"w") as fo:
        fo.write(text)
    cmd = "NuSMV {} > tmp/results.out".format(path)
    os.system(cmd)
    results = ""
    with open("tmp/results.out",'r') as fo:
        results = fo.read()
    p = re.compile("specification (.*\))[\t ]*is true\n")
    TS = p.findall(results)
    p = re.compile("specification (.*\))[\t ]*is false\n")
    FS = p.findall(results)
    return [TS,FS]

def results_update(R,Ri,i,n,SP,verbose=True):
    for s in Ri[0]:
        c_s = SP[s]
        R["SPECS"][c_s][0] += 1
    for s in Ri[1]:
        c_s = SP[s]
        R["SPECS"][c_s][1].append(i)
    if verbose:
        print("iteration {} / {}".format(i+1,n))
        for s in R["SPECS"]:
            print("spec {}: {}/{}".format(R["SPECS"][s][2],R["SPECS"][s][0],i+1))

def results_save(R,name):
    path = "tmp/" + name
    with open(path,'w') as fo:
        json.dump(R,fo)


def test_model(model,k,verbose=True):    
    file_base = ""
    match model:
        case "2pl":
            file_base = "db_2pl_op{}_base".format(str(k))
        case "c2pl":
            file_base = "db_c2pl_op{}_base".format(str(k))
        case "naive":
            file_base = "db_p2_op{}_naive_base".format(str(k))
        case "sched":
            file_base = "db_p2_op{}_sched_base".format(str(k))
    path = file_base + ".smv"
    base_text = get_smv_base(path)
    S = gen_schedules(k)
    print(len(S))
    pprint(S[:4])
    R = {"SPECS":{}}
    start = time()
    R_0 = test_smv(S[0],base_text,0,len(S),k,model)
    finish = time()
    print("{} : {}".format(S[0],finish-start))
    mn = len(S)*(finish - start)/(60)
    hr = mn/60
    print(mn)
    print(hr)
    SP = {}
    c = 0 
    for s in R_0[0]:
        R["SPECS"][c] = [1,[],s]
        SP[s] = c 
        c += 1
    for s in R_0[1]:
        R["SPECS"][c] = [0,[],s]
        SP[s] = c 
        c += 1
    for i in range(1,len(S)):
        R_i = test_smv(S[i],base_text,i,len(S),k,model)
        results_update(R,R_i,i,len(S),SP,verbose)
    R["S"] = S
    finish = time()
    R["time"] = finish-start
    file_name = file_base + ".json"
    results_save(R,file_name)


if __name__ == "__main__":
    mode = sys.argv[1]
    match mode:
        case "tester":
            model = sys.argv[2]
            k = int(sys.argv[3])
            if len(sys.argv) == 5:
                test_model(model,k,False)
            else:
                test_model(model,k)
        case "results":
            name = sys.argv[2]
            path = "tmp/" + name
            with open(path,"r") as fo:
                R = json.load(fo)
                R1 = {}
                for s in R["SPECS"]:
                    R1[s] = [R["SPECS"][s][0],R["SPECS"][s][2]]
                pprint(R1)
                print("time: {}".format(R["time"]))
        case "results_diff":
            name = sys.argv[2]
            i = sys.argv[3]
            j = sys.argv[4]
            path = "tmp/" + name
            with open(path,"r") as fo:
                R = json.load(fo)
                I_i = set(R["SPECS"][i][1])
                I_j = set(R["SPECS"][j][1])
                I = I_i.difference(I_j)
                print(R["SPECS"][i][2])
                print(R["SPECS"][j][2])
                print(I)
        case "results_spec":
            name = sys.argv[2]
            spec = sys.argv[3]
            path = "tmp/" + name
            with open(path,"r") as fo:
                R = json.load(fo)
                I = R["SPECS"][spec][1]
                print(R["SPECS"][spec][2])
                print(I)
        case "test_index":
            model = sys.argv[2]
            k = int(sys.argv[3])
            index = int(sys.argv[4])
            spec = int(sys.argv[5])
            file_base = ""
            match model:
                case "2pl":
                    file_base = "db_2pl_op{}_base".format(str(k))
                case "c2pl":
                    file_base = "db_c2pl_op{}_base".format(str(k))
                case "naive":
                    file_base = "db_p2_op{}_naive_base".format(str(k))
                case "sched":
                    file_base = "db_p2_op{}_sched_base".format(str(k))
            path =  "tmp/" + file_base + ".json"
            with open(path,"r") as fo:
                R = json.load(fo)
                S_i = R["S"][index]
                print(R["SPECS"].keys())
                spec = R["SPECS"][str(spec)][2]
                path = file_base + ".smv"
                base_text = get_smv_base(path)
                S = gen_schedules(k)
                print(len(S))
                pprint(S[:4])
                text = base_text
                text += gen_schedule_smv(S_i,model)
                text += "\n SPEC {}\jn".format(spec)
                smv_file = "test.smv"
                path = "tmp/{}".format(smv_file)
                with open(path,"w") as fo:
                    fo.write(text)
                cmd = "NuSMV {}".format(path)
                print(cmd)
                os.system(cmd)




