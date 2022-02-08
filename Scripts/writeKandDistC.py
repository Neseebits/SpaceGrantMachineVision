import numpy as np
from Source.cameras.cameras import writeKandDistNPZ

if __name__ == '__main__' :
    lk = np.asarray([[10,0,320],[0,10,240],[0,0,1]])
    ld = np.asarray([[0],[0],[0],[0]])
    rk = lk
    rd = ld
    writeKandDistNPZ(lk, rk, ld, rd)