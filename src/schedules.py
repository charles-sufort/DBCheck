from pprint import pprint
def gen_schedules(n):
    print("here")
    S_i = []
    for i in range(8):
        s_i = []
        for j in range(8):
            if i == j:
                s_i.append([1])
            else:
                s_i.append([0])
        S_i.append(s_i)
    print(S_i[0])
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

if __name__ == "__main__":  
    pprint(len(gen_schedules(2)))



