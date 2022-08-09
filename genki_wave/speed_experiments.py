from genki_wave.data import DataPackage, Point3d, Quaternion, Euler3d


dp = DataPackage(
    gyro=Point3d(x=-4.476753234863281, y=24.975353240966797, z=-12.62863540649414),
    acc=Point3d(x=-0.0078125, y=0.42431640625, z=0.897705078125),
    mag=Point3d(x=0.0, y=0.0, z=-0.0),
    raw_pose=Quaternion(
        w=-0.8855273723602295, x=-0.2154131978750229, y=-0.048614680767059326, z=-0.4046018123626709
    ),
    current_pose=Quaternion(
        w=-0.8855273723602295, x=-0.2154131978750229, y=-0.048614680767059326, z=-0.4046018123626709
    ),
    euler=Euler3d(roll=0.4363507032394409, pitch=0.08832869678735733, yaw=-0.8349159359931946),
    linacc=Point3d(x=-0.09602638334035873, y=0.0034686625003814697, z=0.0019823312759399414),
    peak=False,
    peak_norm_velocity=0.0,
    timestamp_us=29422570,
)

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("dp.as_dict_v0()", setup="from __main__ import dp"))
