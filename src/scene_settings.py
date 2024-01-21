import numpy as np

class Light():
    # requires dtype
    def __init__(self,pos: list,color: list) -> None:
        self.pos=np.array(pos,dtype=np.float32)
        self.color=np.array(color,dtype=np.float32)

def get_lights():
    return [
            Light([-10,0,0],[1,1,1]),
            Light([10,0,0],[1,1,1])]
