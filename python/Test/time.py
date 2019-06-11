from time import time
t0 = time()

t=str(time()-t0).split('.')
t[0]='0'*(4-len(t[0]))+t[0]
t[1]=t[1][:6]+'0'*(6-len(t[1][:6]))
