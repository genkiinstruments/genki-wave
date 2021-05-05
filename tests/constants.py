from genki_wave.data.organization import (
    ButtonAction,
    ButtonEvent,
    ButtonId,
    DataPackage,
    Euler3d,
    Point3d,
    Point4d,
)

SERIAL_DATA = [
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
SERIAL_EXPECTED = [
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
        b"\x04\xda\x8fh\x01\x01\x01\x01\x01\x00\x04\x02\x04\x08\x03\x01\x01\x01\x01\x04\x06\xe5@\x00\x04\x03"
        b"\x01i\r\x9c\x8fYA\x84\xf3qA\x19\x9c\x9b\xc1\x04`\xd1>\x04 "
        b"\xbc>\x04\x80Y?\x01\x01\x01\x01\x01\x01\x01\x01"
    ),
    bytearray(
        b"\x01\x01:\x80\xdc\x04t?\xado\t>\xbc\xd5{\xbe\x90\x0f\xc8\xbd\xdc\x04t?\xado\t>\xbc\xd5{"
        b"\xbe\x90\x0f\xc8\xbdE(\xb1>n\xc3\xea>\x9a\x15\x92>`\xfc\t\xbd\xa8\x14\x82=\x80\xadZ<\x01"
    ),
    bytearray(
        b"\x01\x01\x01\x04:zi\x01\x01\x01\x01\x01\x00\x04\x03\x01i\r\xa9]\x11\xc1w%\xc2\xc1,"
        b"Q;?\x04@\xbf>\x01\x03\xcb>\x04@U?\x01\x01\x01\x01\x01\x01\x01\x01\x01\x016\x80\x03\x97s?\xb0j\r"
    ),
    bytearray(
        b">\xaem}\xbep\xe7\xd5\xbd\x03\x97s?\xb0j\r>\xaem}\xbep\xe7\xd5\xbdI\x8f\xb7>\xe8{"
        b"\xea>\xdb\xec\x9a>\x9c}\x8c\xbd\x8c\xe0\xa7=\x04\xb0\xd09\x01\x01\x01\x01\x04\x9adj\x01\x01\x01\x01"
    ),
    bytearray(
        b"\x01\x00\x04\x02\x04\x08\x02\x01\x01\x01\x01\x04\x8c\xe8@\x00\x04\x02\x04\x08\x03\x01\x06\x01\x01\x04"
        b"\x8c\xe8@\x00\x04\x03\x01i\rjW\x92\xc18\x1f\x07BK\xd4\xceA\x04\xc0%?\x04`\x9a>\x04PI?\x01\x01"
    ),
    bytearray(
        b"\x01\x01\x01\x01\x01\x01\x01\x012\x80#4s?\x03\r\x07>\xb3\x84\x84\xbe\x92\xdf\xc9\xbd#4s?\x03\r\x07"
        b">\xb3\x84\x84\xbe\x92\xdf\xc9\xbd\xf16\xb2>\xa9\x11\xf8>p\x1a\x96>\xfe\x0b:>\x08`\xcd"
    ),
    bytearray(
        b"\xb8\x10\x19\x1c\xbd\x01\x01\x01\x01\x04\xfaNk\x01\x01\x01\x01\x01\x00\x04\x02\x04\x08\x03\x01\x01"
        b"\x01\x01\x04x\xea@\x00\x04\x03\x01i\r28gA\xafD\x15A\x8a\xda\xb9\xc1\x04\xc0\xc2>\x04 \xcf>\x04pX"
    ),
]
BLUETOOH_EXPECTED = [
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.DOWN),
    DataPackage(
        gyro=Point3d(x=13.59756088256836, y=15.121952056884766, z=-19.45121955871582),
        accel=Point3d(x=0.408935546875, y=0.367431640625, z=0.849609375),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9531991481781006, x=0.1342150717973709, y=-0.24593251943588257, z=-0.09768593311309814),
        current_pose=Point4d(
            w=0.9531991481781006, x=0.1342150717973709, y=-0.24593251943588257, z=-0.09768593311309814
        ),
        euler=Euler3d(roll=0.34601035714149475, pitch=0.4585222601890564, yaw=0.28532105684280396),
        linear=Point3d(x=-0.03368794918060303, y=0.06351596117019653, z=0.013347029685974121),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=6912570,
    ),
    DataPackage(
        gyro=Point3d(x=-9.085366249084473, y=-24.268293380737305, z=0.7317073345184326),
        accel=Point3d(x=0.37353515625, y=0.396484375, z=0.8330078125),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9515230059623718, x=0.13810229301452637, y=-0.24748870730400085, z=-0.10444533824920654),
        current_pose=Point4d(
            w=0.9515230059623718, x=0.13810229301452637, y=-0.24748870730400085, z=-0.10444533824920654
        ),
        euler=Euler3d(roll=0.35851505398750305, pitch=0.4579765796661377, yaw=0.3025883138179779),
        linear=Point3d(x=-0.06859895586967468, y=0.08197125792503357, z=0.0003980398178100586),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=6972570,
    ),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.UP),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.CLICK),
    DataPackage(
        gyro=Point3d(x=-18.292682647705078, y=33.780487060546875, z=25.85365867614746),
        accel=Point3d(x=0.6474609375, y=0.301513671875, z=0.786376953125),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9500142931938171, x=0.1318855732679367, y=-0.2588249146938324, z=-0.09857095777988434),
        current_pose=Point4d(w=0.9500142931938171, x=0.1318855732679367, y=-0.2588249146938324, z=-0.09857095777988434),
        euler=Euler3d(roll=0.34807541966438293, pitch=0.48450973629951477, yaw=0.2931704521179199),
        linear=Point3d(x=0.1816863715648651, y=-9.79304313659668e-05, z=-0.03810983896255493),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=7032570,
    ),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.DOWN),
]
