
def gen_schedules(n):
    S_ps = [[]]
    for k in range(n):
        for i in range(8):
            S_p = []
            for j in range(8):
                if j == i:
                    S_p.append([1])
                else:
                    S_p.append([0])
            S_ps_old = S_ps
            S_ps = []
            for s_p in S_ps_old:
                for s_p_k in S_p:
                    s_p_new = s_p + s_p_k
                    S_ps.append(s_p_new)
    return S_ps


if __name__ == "__main__":
    print("here")
    print(gen_schedules(2)) 




    
    


