import pytest

from genki_wave.data.organization_elements import Point3d
from genki_wave.data.quaternions import Quaternion, rotate_vector


@pytest.mark.parametrize(
    "point, quat, expected",
    [
        [
            [-0.391845703125, 0.240478515625, 0.881103515625],
            [0.9644286632537842, 0.1391173005104065, 0.210467979311943, -0.0534288547933101],
            [0.02999111998012227, -0.009860081975630458, 0.9933376506944832],
        ],
        [
            [-0.5517578125, 0.34814453125, 0.763916015625],
            [0.9369975328445436, 0.1840094625949859, 0.2790369093418121, -0.0833195820450782],
            [0.009867312032426412, 0.049273887555624396, 1.0033362832973065],
        ],
    ],
)
def test_rotation(point, quat, expected):
    p = Point3d(*point)
    q = Quaternion(*quat)
    expected = Point3d(*expected)

    actual = rotate_vector(p, q)
    pytest.approx(expected.x, actual.x)
    pytest.approx(expected.y, actual.y)
    pytest.approx(expected.z, actual.z)

    # Make sure the rotation uses unit normalized quaternions
    q2 = Quaternion(*[el * 2 for el in quat])
    actual = rotate_vector(p, q2)
    pytest.approx(expected.x, actual.x)
    pytest.approx(expected.y, actual.y)
    pytest.approx(expected.z, actual.z)


def test_quaternion_norm():
    q0 = Quaternion(1.0, 2.0, 3.0, -4.0).normalize()
    q1 = Quaternion(0.01, -0.556, -3.0, -0.002).normalize()
    for q in [q0, q1]:
        assert sum([el ** 2 for el in [q.w, q.x, q.y, q.z]])


def test_quaternion_to_and_from_point():
    p = Point3d(-0.556, -3.0, -0.002)
    q = Quaternion.from_point3d(p)
    assert q == Quaternion(0.0, -0.556, -3.0, -0.002)
    assert p == q.to_point3d()
