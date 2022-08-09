import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point3d:
    x: float
    y: float
    z: float

    def __sub__(self, other):
        return Point3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def as_dict(self, prefix: str = ""):
        return {f"{prefix}x": self.x, f"{prefix}y": self.y, f"{prefix}z": self.z}


@dataclass(frozen=True)
class Euler3d:
    roll: float
    pitch: float
    yaw: float

    def as_dict(self, prefix: str = ""):
        return {f"{prefix}roll": self.roll, f"{prefix}pitch": self.pitch, f"{prefix}yaw": self.yaw}


@dataclass(frozen=True)
class Quaternion:
    w: float
    x: float
    y: float
    z: float

    @classmethod
    def from_point3d(cls, p: Point3d) -> "Quaternion":
        return cls(0, p.x, p.y, p.z)

    def to_point3d(self):
        return Point3d(self.x, self.y, self.z)

    def __mul__(self, other):
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return Quaternion(w, x, y, z)

    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def normalize(self):
        norm = math.sqrt(sum([el**2 for el in [self.w, self.x, self.y, self.z]]))
        return Quaternion(self.w / norm, self.x / norm, self.y / norm, self.z / norm)

    def as_dict(self, prefix: str = ""):
        return {f"{prefix}w": self.w, f"{prefix}x": self.x, f"{prefix}y": self.y, f"{prefix}z": self.z}


def rotate_vector(p: Point3d, q: Quaternion) -> Point3d:
    """Rotate point p by quaternion q"""
    q = q.normalize()
    p = Quaternion.from_point3d(p)
    p_rot = q * p * q.conjugate()
    return p_rot.to_point3d()
