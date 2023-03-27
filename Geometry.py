from math import acos, sqrt
from typing import *


class Quaternion:
    x: float
    y: float
    z: float
    w: float

    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __mul__(self, other):
        return Quaternion(
            self.x * other.x - self.y * other.y - self.z * other.z - self.w * other.w,
            self.x * other.y + self.y * other.x + self.z * other.w - self.w * other.z,
            self.x * other.z + self.z * other.x + self.w * other.y - self.y * other.w,
            self.x * other.w + self.w * other.x + self.y * other.z - self.z * other.y
        )

    def conjugate(self):
        return Quaternion(self.x, -self.y, -self.z, -self.w)


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

    def rotate(self, quat: Quaternion):
        quaternion_form = quat * Quaternion(0, self.x, self.y, self.z) * quat.conjugate()
        return Vector3(quaternion_form.y, quaternion_form.z, quaternion_form.w)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __div__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)
