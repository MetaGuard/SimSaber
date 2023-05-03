import math
from typing import *

DEG_TO_RAD = 0.0174532924
PI = 3.14159274
RAD_TO_DEG = 57.29578

class Vector3:
    x: float
    y: float
    z: float

class Quaternion:
    x: float
    y: float
    z: float
    w: float

class Matrix3:
    data: list[list[float]]

def clamp(value: float, min: float, max: float) -> float:
      if value < min:
        value = min
      elif value > max:
        value = max
      return value


class Vector3(Vector3):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
# public static Vector3 Cross(Vector3 lhs, Vector3 rhs) => new Vector3((lhs.y * rhs.z - lhs.z * rhs.y), (lhs.z * rhs.x - lhs.x * rhs.z), (lhs.x * rhs.y - lhs.y * rhs.x));
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other: Vector3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def abs(self) -> Vector3:
        return Vector3(math.abs(self.x), math.abs(self.y), math.abs(self.z))

    def sqr_mag(self):
        return self.dot(self)

    def mag(self):
        return math.sqrt(self.sqr_mag())

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @staticmethod
    def normalize(value: Vector3) -> Vector3:
        num = value.magnitude()
        return value / num if num > 0 else Vector3(0.0, 0.0, 0.0)
    
    @staticmethod
    def uunit(index):
        if index == 0:
            return Vector3(1, 0, 0)
        elif index == 1:
            return Vector3(0, 1, 0)
        elif index == 2:
            return Vector3(0, 0, 1)
        else:
            raise ValueError("Index must be between 0 and 2")

    def unit(self) -> Vector3:
        mag = self.magnitude()
        return self / mag

    # def project_onto(self, other: Vector3) -> Vector3:
    #     other_unit = other.unit()
    #     return other_unit * self.dot(other_unit)
    
    def project_onto(self, v: Vector3) -> float:
        projection_length = (self.x * v.x + self.y * v.y + self.z * v.z) / v.magnitude()
        return projection_length

    def normal(self):
        magnitude = self.mag()
        return Vector3(0, 0, 0) if magnitude < 9.9999997473787516E-06 else self / magnitude

    def angle(self, other: Quaternion):
        divisor = math.sqrt(self.sqr_mag() * other.sqr_mag())
        return math.acos(clamp(self.dot(other) / divisor, -1, 1)) * RAD_TO_DEG if divisor > 0 else 0

    def rotate(self, quat: Quaternion):
        quaternion_form = quat * Quaternion(self.x, self.y, self.z, 0) * quat.conjugate()
        return Vector3(quaternion_form.x, quaternion_form.y, quaternion_form.z)

    def __add__(self, other):
        # if type(other) is Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        # else:
        #     return Vector3(self.x + other, self.y + other, self.z + other)

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            raise TypeError("Unsupported type for multiplication with Vector3")

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


class Quaternion(Quaternion):

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
    
    def multiply_point(self, point):
        num1 = self.x * 2.0
        num2 = self.y * 2.0
        num3 = self.z * 2.0
        num4 = self.x * num1
        num5 = self.y * num2
        num6 = self.z * num3
        num7 = self.x * num2
        num8 = self.x * num3
        num9 = self.y * num3
        num10 = self.w * num1
        num11 = self.w * num2
        num12 = self.w * num3

        x = (1.0 - (num5 + num6)) * point.x + (num7 - num12) * point.y + (num8 + num11) * point.z
        y = (num7 + num12) * point.x + (1.0 - (num4 + num6)) * point.y + (num9 - num10) * point.z
        z = (num8 - num11) * point.x + (num9 + num10) * point.y + (1.0 - (num4 + num5)) * point.z

        return Vector3(x, y, z)

    def __truediv__(self, scalar):
        return Quaternion(self.x / scalar, self.y / scalar, self.z / scalar, self.w / scalar)

    def __repr__(self):
        return "/{0}, {1}, {2}, {3}/".format(self.x, self.y, self.z, self.w)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)
    
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def unit(self):
        mag = self.magnitude()
        return Quaternion(self.x / mag, self.y / mag, self.z / mag, self.w / mag)

    def inverse(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w).unit()

    def dot(self, q):
        return self.x * q.x + self.y * q.y + self.z * q.z + self.w * q.w
    
    def to_matrix(self):
        x2 = self.x + self.x
        y2 = self.y + self.y
        z2 = self.z + self.z
        xx = self.x * x2
        xy = self.x * y2
        xz = self.x * z2
        yy = self.y * y2
        yz = self.y * z2
        zz = self.z * z2
        wx = self.w * x2
        wy = self.w * y2
        wz = self.w * z2

        return Matrix3([
            [1.0 - (yy + zz), xy - wz, xz + wy],
            [xy + wz, 1.0 - (xx + zz), yz - wx],
            [xz - wy, yz + wx, 1.0 - (xx + yy)],
        ])

    def rotate(self, vector) -> Vector3:
        matrix = self.to_matrix()
        return matrix * vector

    # https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions#Rotation_matrix_%E2%86%94_quaternion
    @staticmethod
    def from_rotation_matrix(M):
        w = math.sqrt(1 + M[0][0] + M[1][1] + M[2][2]) / 2
        x = (M[2][1] - M[1][2]) / (4 * w)
        y = (M[0][2] - M[2][0]) / (4 * w)
        z = (M[1][0] - M[0][1]) / (4 * w)

        return Quaternion(x, y, z, w)
    
    @staticmethod
    def look_rotation(forward: Vector3, up: Vector3) -> Quaternion:
        forward = forward.normal()
        
        # First matrix column
        side_axis = Vector3.normalize(Vector3.cross(up, forward))
        # Second matrix column
        rotated_up = Vector3.cross(forward, side_axis)
        # Third matrix column
        look_at = forward

        # Sums of matrix main diagonal elements
        trace1 = 1 + side_axis.x - rotated_up.y - look_at.z
        trace2 = 1 - side_axis.x + rotated_up.y - look_at.z
        trace3 = 1 - side_axis.x - rotated_up.y + look_at.z

        # If orthonormal vectors form identity matrix, then return identity rotation
        calculations_epsilon = 1e-15
        if trace1 + trace2 + trace3 < calculations_epsilon:
            return Quaternion(0, 0, 0, 1)

        # Choose largest diagonal
        if trace1 + calculations_epsilon > trace2 and trace1 + calculations_epsilon > trace3:
            s = math.sqrt(trace1) * 2.0
            return Quaternion(
                0.25 * s,
                (rotated_up.x + side_axis.y) / s,
                (look_at.x + side_axis.z) / s,
                (rotated_up.z - look_at.y) / s
            )
        elif trace2 + calculations_epsilon > trace1 and trace2 + calculations_epsilon > trace3:
            s = math.sqrt(trace2) * 2.0
            return Quaternion(
                (rotated_up.x + side_axis.y) / s,
                0.25 * s,
                (look_at.y + rotated_up.z) / s,
                (look_at.x - side_axis.z) / s
            )
        else:
            s = math.sqrt(trace3) * 2.0
            return Quaternion(
                (look_at.x + side_axis.z) / s,
                (look_at.y + rotated_up.z) / s,
                0.25 * s,
                (side_axis.y - rotated_up.x) / s
            )
    
    def forward(self):
        return Vector3(2 * (self.x * self.z - self.w * self.y),
                2 * (self.y * self.z + self.w * self.x),
                1 - 2 * (self.x * self.x + self.y * self.y))
    
    # def forward(self) -> Vector3:
    #     forward_vector = Vector3(0, 0, -1)  # Assuming Z- as the forward direction in a right-handed coordinate system
    #     return self.rotate(forward_vector)

    @staticmethod
    def Slerp(q0, q1, u):
        if u < 0:
            u = 0
        if u > 1:
            u = 1

        θ = math.acos(q0.dot(q1))
        if θ == 0:
            return q0
        output = (math.sin((1 - u) * θ) / math.sin(θ)) * q0 + (math.sin(u * θ) / math.sin(θ)) * q1
        return output / math.sqrt(output.dot(output))
    
    def normalized(self) -> Quaternion:
        norm = math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)
        return Quaternion(self.x / norm, self.y / norm, self.z / norm, self.w / norm)
    
    @staticmethod
    def slerp(q1: Quaternion, q2: Quaternion, t: float) -> Quaternion:
        # Compute the cosine of the angle between the two quaternions
        cos_half_theta = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z

        # If q1 is the same as q2 (or q2 is the inverse of q1), return q1
        if abs(cos_half_theta) >= 1.0:
            return Quaternion(q1.x, q1.y, q1.z, q1.w)

        # If q1 and q2 are in opposite directions, negate q2 to make the interpolation shorter
        if cos_half_theta < 0:
            q2 = Quaternion(-q2.x, -q2.y, -q2.z, -q2.w)
            cos_half_theta = -cos_half_theta

        # If the angle between q1 and q2 is too small, use linear interpolation to avoid numerical instability
        if cos_half_theta > 0.95:
            result = Quaternion(
                q1.x * (1 - t) + q2.x * t,
                q1.y * (1 - t) + q2.y * t,
                q1.z * (1 - t) + q2.z * t,
                q1.w * (1 - t) + q2.w * t,
            )
            return result.normalized()

        # Calculate the actual angle between q1 and q2
        half_theta = math.acos(cos_half_theta)
        sin_half_theta = math.sqrt(1 - cos_half_theta * cos_half_theta)

        # Calculate the scale factors for q1 and q2
        a = math.sin((1 - t) * half_theta) / sin_half_theta
        b = math.sin(t * half_theta) / sin_half_theta

        # Compute the resulting quaternion
        return Quaternion(
            q1.x * a + q2.x * b,
            q1.y * a + q2.y * b,
            q1.z * a + q2.z * b,
            q1.w * a + q2.w * b,
        )

    @staticmethod
    def Lerp(q0, q1, u):
        if u < 0:
            u = 0
        if u > 1:
            u = 1

        output = q0 + (q1 - q0) * u
        return output / math.sqrt(output.dot(output))

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    @staticmethod
    def from_Euler(yaw, pitch, roll):
        yaw *= DEG_TO_RAD
        pitch *= DEG_TO_RAD
        roll *= DEG_TO_RAD

        yawOver2 = yaw * 0.5
        cosYawOver2 = math.cos(yawOver2)
        sinYawOver2 = math.sin(yawOver2)
        pitchOver2 = pitch * 0.5
        cosPitchOver2 = math.cos(pitchOver2)
        sinPitchOver2 = math.sin(pitchOver2)
        rollOver2 = roll * 0.5
        cosRollOver2 = math.cos(rollOver2)
        sinRollOver2 = math.sin(rollOver2)
        result = Quaternion(0, 0, 0, 0)
        result.w = cosYawOver2 * cosPitchOver2 * cosRollOver2 + sinYawOver2 * sinPitchOver2 * sinRollOver2
        result.x = sinYawOver2 * cosPitchOver2 * cosRollOver2 + cosYawOver2 * sinPitchOver2 * sinRollOver2
        result.y = cosYawOver2 * sinPitchOver2 * cosRollOver2 - sinYawOver2 * cosPitchOver2 * sinRollOver2
        result.z = cosYawOver2 * cosPitchOver2 * sinRollOver2 - sinYawOver2 * sinPitchOver2 * cosRollOver2

        return Quaternion(result.x, result.y, result.z, result.w)

    # https://stackoverflow.com/questions/12088610/conversion-between-euler-quaternion-like-in-unity3d-engine
    def to_Euler(self):
        unit = self.dot(self)

        test = self.x * self.w - self.y * self.z
        v = Vector3(0, 0, 0)

        if test > 0.4995 * unit:
            v.x = PI / 2
            v.y = 2 * math.atan2(self.y, self.x)
            v.z = 0

        elif test < -0.4995 * unit:
            v.x = -PI / 2
            v.y = -2 * math.atan2(self.y, self.x)
            v.z = 0

        else:
            v.x = math.asin(2 * (self.w * self.x - self.y * self.z))
            v.y = math.atan2(2 * self.w * self.y + 2 * self.z * self.x, 1 - 2 * (self.x * self.x + self.y * self.y))
            v.z = math.atan2(2 * self.w * self.z + 2 * self.x * self.y, 1 - 2 * (self.z * self.z + self.x * self.x))

        v *= RAD_TO_DEG
        v.x %= 360
        v.y %= 360
        v.z %= 360

        return v
    
class Matrix3(Matrix3):
    def __init__(self, data=None):
        if data is None:
            self.data = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            self.data = data
    
    def __mul__(self, vector: Vector3) -> Vector3:
        x = vector.x * self.data[0][0] + vector.y * self.data[0][1] + vector.z * self.data[0][2]
        y = vector.x * self.data[1][0] + vector.y * self.data[1][1] + vector.z * self.data[1][2]
        z = vector.x * self.data[2][0] + vector.y * self.data[2][1] + vector.z * self.data[2][2]
        return Vector3(x, y, z)
    
    def transpose(self):
        transposed_data = [
            [self.data[0][0], self.data[1][0], self.data[2][0]],
            [self.data[0][1], self.data[1][1], self.data[2][1]],
            [self.data[0][2], self.data[1][2], self.data[2][2]],
        ]
        return Matrix3(transposed_data)
    
    def column(self, index):
        if index < 0 or index > 2:
            raise ValueError("Column index must be between 0 and 2")
        return Vector3(self.data[0][index], self.data[1][index], self.data[2][index])

class Ray:
    origin: Vector3
    direction: Vector3

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = Vector3.normalize(direction)

    def get_point(self, distance):
        return self.origin + self.direction * distance

class Plane:
    normal: Vector3
    distance: float

    def __init__(self, in_normal, in_point_or_d):
        if isinstance(in_point_or_d, Vector3):
            self.normal = Vector3.normalize(in_normal)
            self.distance = Vector3.normalize(in_normal).dot(in_point_or_d) * -1
        else:
            self.normal = Vector3.normalize(in_normal)
            self.distance = in_point_or_d

    @classmethod
    def from_3_points(cls, a, b, c):
        normal = Vector3.normalize(Vector3.cross(b - a, c - a))
        return cls(normal, a)

    def set_normal_and_position(self, in_normal, in_point):
        self.normal = Vector3.normalize(in_normal)
        self.distance = -in_normal.dot(in_point)

    def set_3_points(self, a, b, c):
        self.normal = Vector3.normalize(Vector3.cross(b - a, c - a))
        self.distance = -self.normal.dot(a)

    def flip(self):
        self.normal = -self.normal
        self.distance = -self.distance

    def flipped(self):
        return Plane(-self.normal, -self.distance)

    def translate(self, translation):
        self.distance += self.normal.dot(translation)

    @staticmethod
    def translate_plane(plane, translation):
        return Plane(plane.normal, plane.distance + plane.normal.dot(translation))

    def closest_point_on_plane(self, point):
        num = self.normal.dot(point) + self.distance
        return point - self.normal * num

    def get_distance_to_point(self, point):
        return self.normal.dot(point) + self.distance

    def get_side(self, point):
        return self.normal.dot(point) + self.distance > 0

    def same_side(self, in_pt0, in_pt1):
        distance_to_point1 = self.get_distance_to_point(in_pt0)
        distance_to_point2 = self.get_distance_to_point(in_pt1)
        return (distance_to_point1 > 0 and distance_to_point2 > 0) or (distance_to_point1 <= 0 and distance_to_point2 <= 0)

    def raycast(self, ray: Ray):
        a = ray.direction.dot(self.normal)
        num = -ray.origin.dot(self.normal) - self.distance

        if math.isclose(a, 0.0):
            return False, 0.0

        enter = num / a
        return enter > 0, enter
    
class Plane2:
    normal: Vector3
    center: Vector3

    def __init__(self, normal, center):
        self.normal = normal
        self.center = center

    def side(self, point):
        dot = self.normal.dot(point - self.center)
        if dot > 0:
            return 1
        elif dot < 0:
            return -1
        return 0

    def dist_to_point(self, point):
        return abs(self.line_trace(point, self.normal)[0])

    def line_trace(self, point, dir):
        if self.side(point) == 0:
            return (0, point)

        if self.normal.dot(dir) == 0:
            return (None, None)

        dist = self.normal.dot(self.center - point) / self.normal.dot(dir)
        intersection = point + dist * dir
        return (dist, intersection)

    def ray_trace(self, point, dir):
        dist, output = self.line_trace(point, dir)
        if dist is None or dist < 0:
            return (None, None)
        return (dist, output)



def three_points_to_box(p0: Vector3, p1: Vector3, p2: Vector3):
    normalized1 = ((p1 - p2).cross(p0 - p2)).normal()

    if normalized1.sqr_mag() > 9.9999997473787516e-06:
        normalized2 = (p0 - p1).normal()
        in_normal = normalized2.cross(normalized1)
        orientation = Quaternion.look_rotation(normalized2, normalized1)
        num1 = abs(Plane(in_normal, p0).get_distance_to_point(p2))
        num2 = (p0 - p1).mag()
        vector3 = (p0 + p1) * 0.5
        center = vector3 - in_normal * num1 * 0.5
        half_size = Vector3(num1 * 0.5, 0.0, num2 * 0.5)
        return True, center, half_size, orientation
    else:
        center = Vector3(0, 0, 0)
        half_size = Vector3(0, 0, 0)
        orientation = Quaternion(0, 0, 0, 1)
        return False, center, half_size, orientation
    

def calculate_tip_position(position: Vector3, rotation: Quaternion, distanceFromA: float = 1.0) -> Vector3:
    forward = rotation.forward()
    forward = forward * distanceFromA
    return Vector3(forward.x + position.x, forward.y + position.y, forward.z + position.z)

class Orientation:
    position: Vector3
    rotation: Quaternion

    def __init__(self, pos, rot):
        self.position = pos
        self.rotation = rot

    def inverse_transform_vector(self, vector: Vector3) -> Vector3:
        return vector.rotate(self.rotation.conjugate())
    
class Bounds:
    def __init__(self, center: Vector3, extents: Vector3):
        self.center = center
        self.extents = extents

    def max(self) -> Vector3:
        return self.center + self.extents
    
class Hitbox:
    position: Vector3
    rotation: Quaternion
    size: Vector3
    z_offset: float

    def __init__(self, size, z_offset):
        self.size = size
        self.z_offset = z_offset

    def update(self, orientation: Orientation):
        self.position = Vector3(orientation.position.x, orientation.position.y, orientation.position.z)
        self.rotation = Quaternion(orientation.rotation.x, orientation.rotation.y, orientation.rotation.z, orientation.rotation.w)

        # Calculate the local z-axis direction in world space
        local_z = self.rotation.multiply_point(Vector3(0, 0, 1))

        # Apply the z_offset along the local z-axis direction
        self.position -= local_z * self.z_offset
    
    def get_axes(self): 
        return [ Vector3.normalize(self.rotation.rotate(Vector3(1, 0, 0))),
                Vector3.normalize(self.rotation.rotate(Vector3(0, 1, 0))),
                Vector3.normalize(self.rotation.rotate(Vector3(0, 0, 1))) ]
    
    def project_onto_axis(self, axis): 
        corner_offsets = self.get_corner_offsets()
        return [ 
            min((self.position + offset).dot(axis) for offset in corner_offsets), 
            max((self.position + offset).dot(axis) for offset in corner_offsets) 
        ]

    def get_corner_offsets(self): 
        return [ self.rotation.rotate(Vector3(x, y, z) * self.size * 0.5) for x in [-1, 1] for y in [-1, 1] for z in [-1, 1] ]
    
    def radius(self) -> float:
        extens = self.calculate_aabb_bounds().max()

        return max(extens.x, extens.y, extens.z)
    
    def calculate_aabb_bounds(self) -> Bounds:
        # Calculate the world-space positions of the 8 corners of the OBB
        corners = [
            self.rotation.rotate(Vector3(x, y, z) * self.size * 0.5) + self.position
            for x in [-1, 1]
            for y in [-1, 1]
            for z in [-1, 1]
        ]

        # Find the minimum and maximum values for the x, y, and z components of the corners
        min_corner = Vector3(min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners))
        max_corner = Vector3(max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners))

        # Calculate the center and extents of the AABB
        center = (min_corner + max_corner) * 0.5
        extents = (max_corner - min_corner) * 0.5

        return Bounds(center, extents)