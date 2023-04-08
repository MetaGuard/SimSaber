from math import acos, sqrt, sin
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

    def __rmul__(self, scalar):
        return Quaternion(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    def conjugate(self):
        return Quaternion(self.x, -self.y, -self.z, -self.w)

    def dot(self, q):
        return self.x * q.x + self.y * q.y + self.z * q.z + self.w * q.w

    # https://d3cw3dd2w32x2b.cloudfront.net/wp-content/uploads/2015/01/matrix-to-quat.pdf
    @staticmethod
    def from_rotation_matrix(M):
        if M[2][2] < 0:
            if M[0][0] > M[1][1]:
                t = 1 + M[0][0] - M[1][1] - M[2][2]
                q = Quaternion(t, M[0][1] + M[1][0], M[2][0] + M[0][2], M[1][2] - M[2][1])

            else:
                t = 1 - M[0][0] + M[1][1] - M[2][2]
                q = Quaternion(M[0][1] + M[1][0], t, M[1][2] + M[2][1], M[2][0] - M[0][2])

        else:
            if M[0][0] < -M[1][1]:
                t = 1 - M[0][0] - M[1][1] + M[2][2]
                q = Quaternion(M[2][0] + M[0][2], M[1][2] + M[2][1], t, M[0][1] - M[1][0])

            else:
                t = 1 + M[0][0] + M[1][1] + M[2][2]
                q = Quaternion(M[1][2] - M[2][1], M[2][0] - M[0][2], M[0][1] - M[1][0], t)
        return q * 0.5 / sqrt(t)

    @staticmethod
    def from_forward_and_up(forward, up):
        x_axis = up.cross(forward)
        y_axis = up
        z_axis = forward
        return Quaternion.from_rotation_matrix((
            (x_axis.x, y_axis.x, z_axis.x),
            (x_axis.y, y_axis.y, z_axis.y),
            (x_axis.z, y_axis.z, z_axis.z),
        ))

    @staticmethod
    def Slerp(q0, q1, u):
        θ = acos(q0.dot(q1))
        return (sin((1 - u) * θ) / sin(θ)) * q0 + (sin(u * θ) / sin(θ)) * q1


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
