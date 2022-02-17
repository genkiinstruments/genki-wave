from dataclasses import dataclass


@dataclass(frozen=True)
class Point3d:
    x: float
    y: float
    z: float

    def __sub__(self, other):
        return Point3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)
