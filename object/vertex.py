class Vertex:
    def __init__(self, s=0, t=0, n1=0, n2=0, n3=0, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.s = s
        self.t = t
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

    def to_opengl_format(self):
        return [self.s, self.t,
                self.n1, self.n2, self.n3,
                self.x, self.y, self.z]
