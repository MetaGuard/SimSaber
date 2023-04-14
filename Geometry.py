from math import acos, sqrt, sin, cos, atan2, asin
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

    def __repr__(self):
        return "/{0}, {1}, {2}, {3}/".format(self.x, self.y, self.z, self.w)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def dot(self, q):
        return self.x * q.x + self.y * q.y + self.z * q.z + self.w * q.w

    # https://d3cw3dd2w32x2b.cloudfront.net/wp-content/uploads/2015/01/matrix-to-quat.pdf
    # @staticmethod
    # def from_rotation_matrix(M):
    #     if M[2][2] < 0:
    #         if M[0][0] > M[1][1]:
    #             t = 1 + M[0][0] - M[1][1] - M[2][2]
    #             q = Quaternion(t, M[0][1] + M[1][0], M[2][0] + M[0][2], M[1][2] - M[2][1])

    #         else:
    #             t = 1 - M[0][0] + M[1][1] - M[2][2]
    #             q = Quaternion(M[0][1] + M[1][0], t, M[1][2] + M[2][1], M[2][0] - M[0][2])

    #     else:
    #         if M[0][0] < -M[1][1]:
    #             t = 1 - M[0][0] - M[1][1] + M[2][2]
    #             q = Quaternion(M[2][0] + M[0][2], M[1][2] + M[2][1], t, M[0][1] - M[1][0])

    #         else:
    #             t = 1 + M[0][0] + M[1][1] + M[2][2]
    #             q = Quaternion(M[1][2] - M[2][1], M[2][0] - M[0][2], M[0][1] - M[1][0], t)
    #     return q * 0.5 / sqrt(t)

    # https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions#Rotation_matrix_%E2%86%94_quaternion
    @staticmethod
    def from_rotation_matrix(M):
        w = sqrt(1 + M[0][0] + M[1][1] + M[2][2]) / 2
        x = (M[2][1] - M[1][2]) / (4 * w)
        y = (M[0][2] - M[2][0]) / (4 * w)
        z = (M[1][0] - M[0][1]) / (4 * w)

        return Quaternion(x, y, z, w)

    @staticmethod
    def from_forward_and_up(forward, up):
        x_axis = up.cross(forward).normal()
        y_axis = up.normal()  # forward.cross(x_axis).normal()
        z_axis = x_axis.cross(y_axis).normal()  # forward.normal()
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
        output = (sin((1 - u) * θ) / sin(θ)) * q0 + (sin(u * θ) / sin(θ)) * q1
        return output

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    @staticmethod
    def from_Euler(yaw, roll, pitch):
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
        result.x = cosYawOver2 * cosPitchOver2 * cosRollOver2 + sinYawOver2 * sinPitchOver2 * sinRollOver2
        result.z = sinYawOver2 * cosPitchOver2 * cosRollOver2 + cosYawOver2 * sinPitchOver2 * sinRollOver2
        result.y = cosYawOver2 * sinPitchOver2 * cosRollOver2 - sinYawOver2 * cosPitchOver2 * sinRollOver2
        result.w = cosYawOver2 * cosPitchOver2 * sinRollOver2 - sinYawOver2 * sinPitchOver2 * cosRollOver2

        return Quaternion(result.y, result.z, result.w, result.x)

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    @staticmethod
    def get_Euler(self):
        unit = self.dot(self)

        test = self.x * self.w - self.y * self.z
        v = Vector3(0, 0, 0)

        if test > 0.4995 * unit:
            v.x = PI / 2
            v.y = 2 * atan2(self.y, self.x)
            v.z = 0

        elif test < -0.4995 * unit:
            v.x = -PI / 2
            v.y = -2 * atan2(self.y, self.x)
            v.z = 0

        else:
            v.x = asin(2 * (self.x * self.z - self.w * self.y))
            v.y = atan2(2 * self.x * self.w + 2 * self.y * self.z, 1 - 2 * (self.z * self.z + self.w * self.w))
            v.z = atan2(2 * self.x * self.y + 2 * self.z * self.w, 1 - 2 * (self.y * self.y + self.z * self.z))

        v *= RAD_TO_DEG
        v.x %= 360
        v.y %= 360
        v.z %= 360

        return v

    def to_Euler(self):
        return Quaternion.get_Euler(Quaternion(self.w, self.x, self.y, self.z))

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
            self.y * other.z - self.z * other.y,
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

    def __truediv__(self, scalar):
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


if __name__ == "__main__":
    q = Quaternion(1 / sqrt(30), 2 / sqrt(30), 3 / sqrt(30), 4 / sqrt(30))
    q_q = q * q.conjugate()
    print(q_q.x, q_q.y, q_q.z, q_q.w)
    euler = q.to_Euler()
    q2 = Quaternion.from_Euler(euler.x, euler.y, euler.z)
    print(q.x, q.y, q.z, q.w, q.dot(q))
    print(q2.x, q2.y, q2.z, q2.w, q2.dot(q2))

    print(euler)
    print(q2.to_Euler())
    q = Quaternion.from_forward_and_up(Vector3(3, 0, 4), Vector3(0, 1, 0))
    print("X: ", Vector3(1, 0, 0).rotate(q))
    print("Y: ", Vector3(0, 1, 0).rotate(q))
    print("Z: ", Vector3(0, 0, 1).rotate(q))
