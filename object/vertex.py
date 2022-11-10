class Vertex:
    def __init__(self, s=0, t=0, n1=0, n2=0, n3=0, x=0, y=0, z=0,
                 red=0, green=0, blue=0):
        self.x = x
        self.y = y
        self.z = z
        self.s = s
        self.t = t
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.red = red
        self.green = green
        self.blue = blue

    def to_opengl_texture_format(self):
        return [self.s, self.t,
                self.n1, self.n2, self.n3,
                self.x, self.y, self.z]

    def to_opengl_color_format(self):
        # vertices: format 'C3F_N3F_V3F'
        return [self.red, self.green, self.blue,
                self.n1, self.n2, self.n3,
                self.x, self.y, self.z]

    def to_opengl_coord_format(self):
        # vertices: format 'V3F'
        return [self.x, self.y, self.z]
