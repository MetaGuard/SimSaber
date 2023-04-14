from math import acos, sqrt, sin, cos, atan2
from typing import *

DEG_TO_RAD = 0.0174532924
PI = 3.14159274
RAD_TO_DEG = 57.29578


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
        return Quaternion(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return Quaternion(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, other):
        if type(other) is Quaternion:
            return Quaternion(
                self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                self.w * other.y + self.y * other.w + self.z * other.x - self.x * other.z,
                self.w * other.z + self.z * other.w + self.x * other.y - self.y * other.x,
                self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            )
        else:
            return other * self

    def __rmul__(self, scalar):
        return Quaternion(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    def __truediv__(self, scalar):
        return Quaternion(self.x / scalar, self.y / scalar, self.z / scalar, self.w / scalar)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

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
        if θ == 0:
            return q0
        return (sin((1 - u) * θ) / sin(θ)) * q0 + (sin(u * θ) / sin(θ)) * q1

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    @staticmethod
    def from_Euler(yaw, pitch, roll):
        yaw *= DEG_TO_RAD
        pitch *= DEG_TO_RAD
        roll *= DEG_TO_RAD

        yawOver2 = yaw * 0.5
        cosYawOver2 = cos(yawOver2)
        sinYawOver2 = sin(yawOver2)
        pitchOver2 = pitch * 0.5
        cosPitchOver2 = cos(pitchOver2)
        sinPitchOver2 = sin(pitchOver2)
        rollOver2 = roll * 0.5
        cosRollOver2 = cos(rollOver2)
        sinRollOver2 = sin(rollOver2)
        result = Quaternion(0, 0, 0, 0)
        result.w = cosYawOver2 * cosPitchOver2 * cosRollOver2 + sinYawOver2 * sinPitchOver2 * sinRollOver2
        result.x = sinYawOver2 * cosPitchOver2 * cosRollOver2 + cosYawOver2 * sinPitchOver2 * sinRollOver2
        result.y = cosYawOver2 * sinPitchOver2 * cosRollOver2 - sinYawOver2 * cosPitchOver2 * sinRollOver2
        result.z = cosYawOver2 * cosPitchOver2 * sinRollOver2 - sinYawOver2 * sinPitchOver2 * cosRollOver2

        return result

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    def to_Euler(self):
        sqw = self.w * self.w
        sqx = self.x * self.x
        sqy = self.y * self.y
        sqz = self.z * self.z
        unit = sqx + sqy + sqz + sqw

        test = self.x * self.w - self.y * self.z
        v = Vector3(0, 0, 0)

        if test > 0.4995 * unit:
            v.x = 2 * atan2(self.y, self.x)
            v.y = PI / 2
            v.z = 0
            return normalize_angles(v * RAD_TO_DEG)

        if test < -0.4995 * unit:
            v.x = -2 * atan2(self.y, self.x)
            v.y = -PI / 2
            v.z = 0
            return normalize_angles(v * RAD_TO_DEG)

        v.x = atan2(2 * self.x * self.w + 2 * self.y * self.z, 1 - 2 * (self.z * self.z + self.w * self.w))
        v.y = atan2(2 * (self.x * self.z - self.w * self.y))
        v.z = atan2(2 * self.x * self.y + 2 * self.z * self.w, 1 - 2 * (self.y * self.y + self.z * self.z))

        return normalize_angles(v * RAD_TO_DEG)


def normalize_angles(angles):
    angles.x %= 360
    angles.y %= 360
    angles.z %= 360
    return angles


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
        return self.x * other.x + self.y * other.y + self.z * other.z

    def sqr_mag(self):
        return self.dot(self)

    def mag(self):
        return sqrt(self.sqr_mag())

    def normal(self):
        return self / self.mag()

    def angle(self, other):
        return acos(self.dot(other) / sqrt(self.sqr_mag() * other.sqr_mag()))

    def rotate(self, quat: Quaternion):
        quaternion_form = quat * Quaternion(self.x, self.y, self.z, 0) * quat.conjugate()
        return Vector3(quaternion_form.x, quaternion_form.y, quaternion_form.z)

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

    def __str__(self):
        return "<{0}, {1}, {2}>".format(self.x, self.y, self.z)

    def __repr__(self):
        return "<{0}, {1}, {2}>".format(self.x, self.y, self.z)

    @staticmethod
    def distance(v, u):
        return (v - u).mag()


class Orientation:
    position: Vector3
    rotation: Quaternion

    def __init__(self, pos, rot):
        self.position = pos
        self.rotation = rot
