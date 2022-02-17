from typing import Union

from genki_wave.data.organization import ButtonEvent, DataPackage, Point3d, Point4d


def quat_mult(q1: Point4d, q2: Point4d) -> Point4d:
    w1, x1, y1, z1 = q1.w, q1.x, q1.y, q1.z
    w2, x2, y2, z2 = q2.w, q2.x, q2.y, q2.z
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

    return Point4d(w, x, y, z)


def quat_conj(q):
    w, x, y, z = q
    return w, -x, -y, -z


def rotate_vector(x: Point3d, q: Point4d):
    q_conj = quat_conj(q)
    x_quat = [0, x[0], x[1], x[2]]
    out = quat_mult(quat_mult(q, x_quat), q_conj)
    return out[1:]


def acc_global(data: Union[DataPackage, ButtonEvent]):
    data
    pass
