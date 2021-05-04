from genki_wave.data.organization import (
    ButtonAction,
    ButtonEvent,
    ButtonId,
    DataPackage,
    Euler3d,
    Point3d,
    Point4d,
)

DATA = [
    b"\r7,R\xc2\xa1V:\xc2\x16W\x9eB\x04`\x8e>\x04PR?0\x90\x11?\xf7\xa5_?n\x16\xe6>#\xb6\xb7\xbds\xaa\x1c>"
    b"\xf7\xa5_?n\x16\xe6>#\xb6\xb7\xbds\xaa\x1c>\xd0\xe0j?0\xea\x98>\xad_I\xbe\x08m\x84\xbc\x08\xa1\x82=\x04"
    b"\x93\x98\xbb\x01\x01\x01\x01\x05\x8c\xf0\xb9\x98\x01\x01\x01\x01\x00\x04\x03\x01]\r\xfc\x92\x91\xc2\x82"
    b"\xd30\xc2\xeb\x05\x83B",
    b"\x04`\x8f>\x04\x90J?0@\xfd>+\xbf_?\x1ai\xe5>\x1b=\xbb\xbd\xbbW\x1d>+\xbf_?\x1ai\xe5>\x1b=\xbb\xbd"
    b"\xbbW\x1d>\x12\x14j?\x83\xaa\x9a>\x06\x8eI\xbe\x0c1\x8f\xbc\xd0\xf6\x13=p\x9e\xa4\xbd\x01\x01\x01\x01"
    b"\x05P\xfa\xb9\x98\x01\x01\x01\x01\x00\x04\x02\x04\x08\x01\x02\x01\x01\x01\x04\x82\xbe@\x00\x04\x03"
    b"\x01]\r\xadQj\xc2\xad$B\xc2\xd2i\x8cB\x01\x03\xad>\x04\xa06?\x01;\xf5>\x1d\xe5_",
    b"?\x8a/\xe4>\xb0\xbb\xc2\xbd\xfe\xcf\x1e>\x1d\xe5_?\x8a/\xe4>\xb0\xbb\xc2\xbd\xfe\xcf\x1e>6\xa0h?"
    b"\xa9s\x9e>\x8e\xe2I\xbe\xf8\x85\x08=\x10L\x16\xbd\xc0\x94\xcb\xbd\x01\x01\x01\x01\x05\xd8\r\xba\x98"
    b"\x01\x01\x01\x01\x00\x04\x03\x01]\r*^h\xc2\xc0\xd9C\xc2\xe4\x1e\x89B\x04\x80\xaf>\x01\x03&?<\xc0\xf3>"
    b"\x16\xf3_?\xdd\xa2\xe3><\x84\xc6\xbd\x13\x90\x1f>\x16\xf3_?\xdd\xa2\xe3><\x84\xc6\xbd\x13\x90\x1f>",
    b"\xe7\xf8g?)b\xa0>\x04\tJ\xbe0\xd0\r=@:\xcb\xbd\xb8\n\xd3\xbd\x01\x01\x01\x01\x05\x9c\x17\xba\x98"
    b"\x01\x01\x01\x01\x00\x04\x03\x01]\rV\xafe\xc2\xc0\xd9C\xc2V]\x84B\x04@\xb3>\x04`\x15?\x01;\xf4>j"
    b"\x01`?\t\x15\xe3>\xadG\xca\xbd\xa0G >j\x01`?\t\x15\xe3>\xadG\xca\xbd\xa0G >\xd1Pg?}J\xa2>H%J\xbe"
    b"\xf0M\x1d=L\xa5%\xbe8\x81\xd4\xbd\x01\x01\x01\x01\x05",
]
EXPECTED = [
    DataPackage(
        gyro=Point3d(x=-72.78707885742188, y=-44.20655059814453, z=65.51155853271484),
        accel=Point3d(x=0.280029296875, y=0.791259765625, z=0.49462890625),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.8740107417106628, x=0.44806748628616333, y=-0.09142514318227768, z=0.15365497767925262),
        current_pose=Point4d(
            w=0.8740107417106628, x=0.44806748628616333, y=-0.09142514318227768, z=0.15365497767925262
        ),
        euler=Euler3d(roll=0.914368748664856, pitch=0.3020821511745453, yaw=-0.1968308389186859),
        linear=Point3d(x=-0.017479419708251953, y=0.03612405061721802, z=-0.08038032054901123),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=2562325072,
    ),
    ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.DOWN),
    DataPackage(
        gyro=Point3d(x=-58.57976150512695, y=-48.53581619262695, z=70.20668029785156),
        accel=Point3d(x=0.337890625, y=0.71337890625, z=0.478515625),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.874589741230011, x=0.44567519426345825, y=-0.095084547996521, z=0.1550903022289276),
        current_pose=Point4d(w=0.874589741230011, x=0.44567519426345825, y=-0.095084547996521, z=0.1550903022289276),
        euler=Euler3d(roll=0.9086946249008179, pitch=0.30947616696357727, yaw=-0.19715330004692078),
        linear=Point3d(x=0.03333088755607605, y=-0.03669363260269165, z=-0.09940481185913086),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=2562330072,
    ),
    DataPackage(
        gyro=Point3d(x=-58.091957092285156, y=-48.962646484375, z=68.56033325195312),
        accel=Point3d(x=0.3427734375, y=0.6484375, z=0.47607421875),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.8748029470443726, x=0.4446019232273102, y=-0.09693190455436707, z=0.15582303702831268),
        current_pose=Point4d(w=0.8748029470443726, x=0.4446019232273102, y=-0.09693190455436707, z=0.15582303702831268),
        euler=Euler3d(roll=0.9061416983604431, pitch=0.3132489025592804, yaw=-0.1973000168800354),
        linear=Point3d(x=0.034622371196746826, y=-0.09923219680786133, z=-0.10304778814315796),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=2562332572,
    ),
]


BLUETOOTH_DATA = [
    bytearray(
        b"\x03\x01]\x00\x83\xec\xbe@HF\x92A,\xcd\xa9>\x00\xa0,?\x00\x00\x17?\x00\xa0\x98>|\x93I?-\xf5\xdd>\x8d\x9a"
        b"\xd1\xbe\xde\xb7\x14>|\x93I?-\xf5\xdd>\x8d\x9a\xd1\xbe\xde\xb7\x14>\xaep\x8c?\x84;a?t\xd3L> ;\xc5\xbd@s"
        b"\xd5< 0\x82<\x00\x00\x00\x00\x00\xb8\xe6\x193\x00\x00\x00\x00"
    ),
    bytearray(
        b"\x03\x01]\x00>\xff\x93@\xf3\xfc\x1aAP\xb2\x15A\x00 !?\x00\x90\x13?\x00\x00<>\x95\x9cI?\xa8\x0e\xde>3."
        b"\xd1\xbe\xca\xbb\x15>\x95\x9cI?\xa8\x0e\xde>3.\xd1\xbe\xca\xbb\x15>\x98>\x8c?\x90\x1fa?\xf5*I>LV\x10"
        b"\xbe@@Q<@\x08\xcc\xbd\x00\x00\x00\x00\x00\xc8\r\x1a3\x00\x00\x00\x00"
    ),
    bytearray(
        b"\x03\x01]\x00\x96\x9a\x17@$\x96B@J\xcbaA\x000\x1b?\x00\xd0\x04?\x00\x009>\xb8\x98I?\x9f\x08\xde>?7\xd1"
        b"\xbe)\x00\x16>\xb8\x98I?\x9f\x08\xde>?7\xd1\xbe)\x00\x16>\xaa7\x8c?\xa9;a?\x13\xaaH>\xf0](\xbe\x9096\xbd"
        b"\xf0\xf6\xd1\xbd\x00\x00\x00\x00\x00\x8c\x17\x1a3\x00\x00\x00\x00"
    ),
    bytearray(b"\x02\x04\x08\x00\x00\x01\x00\x00PzrC"),
]
BLUETOOTH_EXPECTED = [
    DataPackage(
        gyro=Point3d(x=5.966371059417725, y=18.284317016601562, z=0.3316434621810913),
        accel=Point3d(x=0.67431640625, y=0.58984375, z=0.298095703125),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.7874066829681396, x=0.4335111677646637, y=-0.40938225388526917, z=0.1452326476573944),
        current_pose=Point4d(w=0.7874066829681396, x=0.4335111677646637, y=-0.40938225388526917, z=0.1452326476573944),
        euler=Euler3d(roll=1.0971887111663818, pitch=0.8798143863677979, yaw=0.20002537965774536),
        linear=Point3d(x=-0.09630417823791504, y=0.02605593204498291, z=0.015892088413238525),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=857335480,
    ),
    DataPackage(
        gyro=Point3d(x=4.624907493591309, y=9.686755180358887, z=9.356033325195312),
        accel=Point3d(x=0.62939453125, y=0.576416015625, z=0.18359375),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.7875455021858215, x=0.43370556831359863, y=-0.4085555970668793, z=0.14622417092323303),
        current_pose=Point4d(w=0.7875455021858215, x=0.43370556831359863, y=-0.4085555970668793, z=0.14622417092323303),
        euler=Euler3d(roll=1.0956602096557617, pitch=0.8793878555297852, yaw=0.19645293056964874),
        linear=Point3d(x=-0.14095419645309448, y=0.012771666049957275, z=-0.0996251106262207),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=857345480,
    ),
    DataPackage(
        gyro=Point3d(x=2.3688101768493652, y=3.0404138565063477, z=14.112131118774414),
        accel=Point3d(x=0.606201171875, y=0.518798828125, z=0.1806640625),
        mag=Point3d(x=0.0, y=0.0, z=0.0),
        raw_pose=Point4d(w=0.7874865531921387, x=0.43365952372550964, y=-0.4086246192455292, z=0.14648498594760895),
        current_pose=Point4d(w=0.7874865531921387, x=0.43365952372550964, y=-0.4086246192455292, z=0.14648498594760895),
        euler=Euler3d(roll=1.0954487323760986, pitch=0.8798165917396545, yaw=0.19596128165721893),
        linear=Point3d(x=-0.16442084312438965, y=-0.044488489627838135, z=-0.10252177715301514),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=857347980,
    ),
    ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.DOWN),
]
