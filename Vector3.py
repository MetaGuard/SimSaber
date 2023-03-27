from math import acos, sqrt


class Vector3:
    x: float
    y: float
    z: float

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.z,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        return self.x * other.x + self.y + other.y + self.z * other.z

    def sqr_mag(self):
        return self.dot(self)

    def mag(self):
        return sqrt(self.sqr_mag())

    def normal(self):
        return self / self.mag()

    def angle(self, other):
        return acos(self.dot(other) / sqrt(self.sqr_mag() * other.sqr_mag()))

    def __add__(self, other):
        if type(other) is not Vector3:
            raise TypeError

        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __div__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
