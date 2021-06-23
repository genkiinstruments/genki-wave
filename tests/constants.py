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
    b"\x012\x807\x87b\xbfrL^\xbe\x12\t>\xbd\x8e\x8f\xcf\xbe7\x87b\xbfrL^\xbe\x12\t>\xbd\x8e\x8f\xcf\xbeQ\x15\xe0>3"
    b"\x99\xc0=\x1e\xeaU\xbf8B\xf9\xbc\x08\x18;\xb9\xa0X\xe9\xbc\x01\x01\x01\x01\x05\xda\xcc\xc0\x01\x01\x01\x01\x01"
    b"\x00\x04\x03\x01i\r\x90A\x8f\xc0\x86\xcd\xc7A\xe4\x0eJ\xc1\x01\x01\x02\xbc\x04@\xd9>\x04\xd0e?\x01\x01\x01\x01"
    b"\x01\x01\x01\x01\x01\x016\x80\xec\xb1b\xbfG\x95\\\xbe0 G\xbd\xf8'",
    b"\xcf\xbe\xec\xb1b\xbfG\x95\\\xbe0 G\xbd\xf8'\xcf\xbe\\i\xdf>\xad\xe5\xb4=\r\xbdU\xbf{"
    b"\xa9\xc4\xbd\x80Rc;\x04\xea\x01;\x01\x01\x01\x01\x05\xea\xf3\xc0\x01\x01\x01\x01\x01\x00\x04\x02\x04\x08\x01"
    b"\x02\x01\x01\x01\x04y\xeeA\x00\x04\x03\x01i\r\xf3q%A\x07\xb4CA<t\tA\x01\x03\x83=\x01\x03\xc4>\x04\xb0d?\x01\x01"
    b"\x01\x01\x01\x01\x01\x01\x01\x016\x80\x11\xa2b\xbf\r\xda[\xbe\x98\x01U\xbd\xd9g\xcf\xbe\x11",
    b"\xa2b\xbf\r\xda[\xbe\x98\x01U\xbd\xd9g\xcf\xbe\xea\x16\xe0>\xd7\xda\xa7=\x8d_V\xbf\xf8\xaa\x92\xbc "
    b"\xa0!\xbd\x04\xa7\x19\xbb\x01\x01\x01\x01\x05\nB\xc1\x01\x01\x01\x01\x01\x00\x04\x03\x01i\r,"
    b"\x91HA~\xa6\xdd@zz\x08A\x01\x03\xd0=\x04@\xc4>\x04\xc0r?\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01:\x80\xa3}b\xbf"
    b"\x8d\\\\\xbe\xec\x9dX\xbd]\xd5\xcf\xbe\xa3}b\xbf\x8d\\\\\xbe\xec\x9dX\xbd]\xd5\xcf\xbe:\xe5",
    b"\xe0>\x12V\xa6=,\xebV\xbf\xecb\xa7<\x08\x8b%\xbd\xe0\xe7Y=\x01\x01\x01\x01\x05\x1ai\xc1\x01\x01\x01\x01\x01\x00"
    b"\x04\x03\x01i\r\x8az\x84A\xd0\xfb\x7f@\x86y#@\x01\x03\r>\x04`\xe0>\x04\xe0}?\x01\x01\x01\x01\x01\x01\x01\x01"
    b"\x01\x01:\x80\xf5^b\xbf\xd0]]\xbe\xd9[[\xbd*\x0b\xd0\xbe\xf5^b\xbf\xd0]]\xbe\xd9[[\xbd*\x0b\xd0\xbe(\x19\xe2",
    b">\xd3\x01\xa6=R3W\xbfdYh=\x80\x11K<\xb0\xfa\xc7=\x01\x01\x01\x01\x05*\x90\xc1\x01\x01\x01\x01\x01\x00\x04\x03"
    b"\x01i\r,\xf1\x99A_\xf1\x98?\x7f\x92\x1f@\x04\x80\xff=\x04\x80\xf4>\x04\x90t?\x01\x01\x01\x01\x01\x01\x01\x01"
    b"\x01\x01:\x80\xb8Bb\xbf\x18\xcc^\xbe8c^\xbdr\x17\xd0\xbe\xb8Bb\xbf\x18\xcc^\xbe8c^\xbdr\x17\xd0\xbe\x88\xbe\xe3"
    b">I\xd5\xa5=5OW\xbf.\xb23=\x18\xe9G=",
    b"\xa8I\x80=\x01\x01\x01\x01\x05:\xb7\xc1\x01\x01\x01\x01\x01\x00\x04\x03\x01i\r8_xA\xae\x10\x0e\xc0\xd6q\xfd"
    b"@\x04\x80\xd8=\x04\x80\xeb>\x04\x10l?\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01:\x80\xe4\x1eb\xbf\xc6N`\xbe<\x17"
    b"`\xbd\x04D\xd0\xbe\xe4\x1eb\xbf\xc6N`\xbe<\x17`\xbd\x04D\xd0\xbeVR\xe5>17\xa7=\xae\x84W\xbfh\xe1\xc5<pY\xe9"
    b"<\xe0r\xfc<\x01\x01\x01\x01\x05J\xde\xc1\x01\x01\x01\x01\x01",
    b"\x00\x04\x03\x01i\r\x06'1A\xf3\x97\xa8\xc0\xbfg3A\x04\x80\xa9=\x04\x80\xdf>\x04@b?\x01\x01\x01\x01\x01\x01\x01"
    b"\x01\x01\x01.\x80!\xf8a\xbf\xfa\x8fa\xbe.\xdd_\xbd\x80\x96\xd0\xbe!\xf8a\xbf\xfa\x8fa\xbe.\xdd_\xbd\x80\x96\xd0"
    b"\xbe\x9bs\xe6>\xe7*\xaa=\xd5\xd6W\xbf\x0c\x98q\xb9\x80uL;\x80T\xd3\xbb\x01\x01\x01\x01\x05Z\x05\xc2\x01\x01\x01"
    b"\x01\x01\x00\x04\x03\x01i\rp\xbe\xb0@K\x07\x07\xc1\x12\xec\x8c",
    b"A\x01\x03\x86=\x04\x80\xd7>\x04\xa0d?\x01\x01\x01\x01\x01\x01\x01\x01\x01\x016\x80H\xcea\xbf\xeayb\xbe\x0e\x9f"
    b"]\xbd\xd0\x15\xd1\xbeH\xcea\xbf\xeayb\xbe\x0e\x9f]\xbd\xd0\x15\xd1\xbe\xb1\n\xe7>z\xac\xae=\xd5LX\xbf "
    b"\xd9\xa1\xbc\x80{\\\xbc\x04.e;\x01\x01\x01\x01\x05j,"
    b"\xc2\x01\x01\x01\x01\x01\x00\x04\x02\x04\x08\x01\x01\x01\x01\x01\x04\x1d\xefA\x00",
    b"\x04\x02\x04\x08\x01\x02\x06\x01\x01\x04\x1d\xefA\x00\x04\x03\x01i\r\x01\xc0:\xc1\xc5\x06\xa7\xc1\n<\x12A\x01"
    b"\x03\xd7=\x04\xa0\xca>\x04\xc0g?\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01:\x80+xa\xbfO\x9fc\xbe\xf3\x83I\xbd\xf8"
    b"\x89\xd2\xbe+xa\xbfO\x9fc\xbe\xf3\x83I\xbd\xf8\x89\xd2\xbe!\xf4\xe5>("
    b"9\xc5=\xfbQY\xbf\xc8\xa6\x10<\xc0\x89\x14\xbd\xa0x\x80<\x01\x01\x01\x01\x05\x9a\xa1\xc2\x01\x01\x01\x01\x01\x00"
    b"\x04\x03\x01",
]
SERIAL_EXPECTED = [
    DataPackage(
        gyro=Point3d(x=-4.476753234863281, y=24.975353240966797, z=-12.62863540649414),
        acc=Point3d(x=-0.0078125, y=0.42431640625, z=0.897705078125),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8855273723602295, x=-0.2154131978750229, y=-0.048614680767059326, z=-0.4046018123626709),
        current_pose=Point4d(
            w=-0.8855273723602295, x=-0.2154131978750229, y=-0.048614680767059326, z=-0.4046018123626709
        ),
        euler=Euler3d(roll=0.4363507032394409, pitch=0.08832869678735733, yaw=-0.8349159359931946),
        linacc=Point3d(x=-0.09602638334035873, y=0.0034686625003814697, z=0.0019823312759399414),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29422570,
    ),
    ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.DOWN),
    DataPackage(
        gyro=Point3d(x=10.340319633483887, y=12.231451988220215, z=8.590877532958984),
        acc=Point3d(x=0.06396484375, y=0.3828125, z=0.893310546875),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8852854371070862, x=-0.21469898521900177, y=-0.05200347304344177, z=-0.4050891697406769),
        current_pose=Point4d(
            w=-0.8852854371070862, x=-0.21469898521900177, y=-0.05200347304344177, z=-0.4050891697406769
        ),
        euler=Euler3d(roll=0.4376748204231262, pitch=0.08196037262678146, yaw=-0.8373954892158508),
        linacc=Point3d(x=-0.01790378987789154, y=-0.03945934772491455, z=-0.0023445487022399902),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29442570,
    ),
    DataPackage(
        gyro=Point3d(x=12.535442352294922, y=6.926573753356934, z=8.529901504516602),
        acc=Point3d(x=0.1015625, y=0.38330078125, z=0.9482421875),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8847295641899109, x=-0.21519680321216583, y=-0.05288498103618622, z=-0.4059247076511383),
        current_pose=Point4d(
            w=-0.8847295641899109, x=-0.21519680321216583, y=-0.05288498103618622, z=-0.4059247076511383
        ),
        euler=Euler3d(roll=0.43924885988235474, pitch=0.08121885359287262, yaw=-0.8395259380340576),
        linacc=Point3d(x=0.020432911813259125, y=-0.040415793657302856, z=0.0531996488571167),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29452570,
    ),
    DataPackage(
        gyro=Point3d(x=16.559833526611328, y=3.999744415283203, z=2.5542922019958496),
        acc=Point3d(x=0.1376953125, y=0.438232421875, z=0.99169921875),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.884261429309845, x=-0.21617817878723145, y=-0.053554389625787735, z=-0.40633517503738403),
        current_pose=Point4d(
            w=-0.884261429309845, x=-0.21617817878723145, y=-0.053554389625787735, z=-0.40633517503738403
        ),
        euler=Euler3d(roll=0.44159817695617676, pitch=0.08105816692113876, yaw=-0.8406268358230591),
        linacc=Point3d(x=0.05672587454319, y=0.012394309043884277, z=0.09764611721038818),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29462570,
    ),
    DataPackage(
        gyro=Point3d(x=19.242759704589844, y=1.1948660612106323, z=2.493316411972046),
        acc=Point3d(x=0.124755859375, y=0.4775390625, z=0.955322265625),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8838305473327637, x=-0.21757543087005615, y=-0.05429384112358093, z=-0.40642887353897095),
        current_pose=Point4d(
            w=-0.8838305473327637, x=-0.21757543087005615, y=-0.05429384112358093, z=-0.40642887353897095
        ),
        euler=Euler3d(roll=0.4448130130767822, pitch=0.08097321540117264, yaw=-0.8410523533821106),
        linacc=Point3d(x=0.04387109726667404, y=0.04880627989768982, z=0.0626404881477356),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29472570,
    ),
    DataPackage(
        gyro=Point3d(x=15.523246765136719, y=-2.2197680473327637, z=7.9201459884643555),
        acc=Point3d(x=0.105712890625, y=0.4599609375, z=0.922119140625),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8832838535308838, x=-0.21905049681663513, y=-0.05470965802669525, z=-0.40676891803741455),
        current_pose=Point4d(
            w=-0.8832838535308838, x=-0.21905049681663513, y=-0.05470965802669525, z=-0.40676891803741455
        ),
        euler=Euler3d(roll=0.44789379835128784, pitch=0.08164823800325394, yaw=-0.8418682813644409),
        linacc=Point3d(x=0.024155333638191223, y=0.028485029935836792, z=0.030816495418548584),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29482570,
    ),
    DataPackage(
        gyro=Point3d(x=11.072027206420898, y=-5.268548488616943, z=11.212828636169434),
        acc=Point3d(x=0.082763671875, y=0.4365234375, z=0.8837890625),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8826923966407776, x=-0.22027578949928284, y=-0.05465429276227951, z=-0.4073982238769531),
        current_pose=Point4d(
            w=-0.8826923966407776, x=-0.22027578949928284, y=-0.05465429276227951, z=-0.4073982238769531
        ),
        euler=Euler3d(roll=0.45010074973106384, pitch=0.08308964222669601, yaw=-0.8431218266487122),
        linacc=Point3d(x=-0.00023040175437927246, y=0.0031197965145111084, z=-0.006449282169342041),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29492570,
    ),
    DataPackage(
        gyro=Point3d(x=5.523246765136719, y=-8.43928050994873, z=17.61526870727539),
        acc=Point3d(x=0.0654296875, y=0.4208984375, z=0.89306640625),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8820538520812988, x=-0.22116819024085999, y=-0.05410676449537277, z=-0.4083695411682129),
        current_pose=Point4d(
            w=-0.8820538520812988, x=-0.22116819024085999, y=-0.05410676449537277, z=-0.4083695411682129
        ),
        euler=Euler3d(roll=0.4512534439563751, pitch=0.08528991043567657, yaw=-0.8449223637580872),
        linacc=Point3d(x=-0.019756853580474854, y=-0.013457179069519043, z=0.003497004508972168),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29502570,
    ),
    ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.UP),
    ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.CLICK),
    DataPackage(
        gyro=Point3d(x=-11.671875953674316, y=-20.878305435180664, z=9.139657974243164),
        acc=Point3d(x=0.10498046875, y=0.395751953125, z=0.9052734375),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=-0.8807398676872253, x=-0.2222874015569687, y=-0.049198102205991745, z=-0.4112088680267334),
        current_pose=Point4d(
            w=-0.8807398676872253, x=-0.2222874015569687, y=-0.049198102205991745, z=-0.4112088680267334
        ),
        euler=Euler3d(roll=0.4491281807422638, pitch=0.09630042314529419, yaw=-0.8489071726799011),
        linacc=Point3d(x=0.008828826248645782, y=-0.03626418113708496, z=0.015682518482208252),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=29532570,
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
        acc=Point3d(x=0.408935546875, y=0.367431640625, z=0.849609375),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9531991481781006, x=0.1342150717973709, y=-0.24593251943588257, z=-0.09768593311309814),
        current_pose=Point4d(
            w=0.9531991481781006, x=0.1342150717973709, y=-0.24593251943588257, z=-0.09768593311309814
        ),
        euler=Euler3d(roll=0.34601035714149475, pitch=0.4585222601890564, yaw=0.28532105684280396),
        linacc=Point3d(x=-0.03368794918060303, y=0.06351596117019653, z=0.013347029685974121),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=6912570,
    ),
    DataPackage(
        gyro=Point3d(x=-9.085366249084473, y=-24.268293380737305, z=0.7317073345184326),
        acc=Point3d(x=0.37353515625, y=0.396484375, z=0.8330078125),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9515230059623718, x=0.13810229301452637, y=-0.24748870730400085, z=-0.10444533824920654),
        current_pose=Point4d(
            w=0.9515230059623718, x=0.13810229301452637, y=-0.24748870730400085, z=-0.10444533824920654
        ),
        euler=Euler3d(roll=0.35851505398750305, pitch=0.4579765796661377, yaw=0.3025883138179779),
        linacc=Point3d(x=-0.06859895586967468, y=0.08197125792503357, z=0.0003980398178100586),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=6972570,
    ),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.UP),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.CLICK),
    DataPackage(
        gyro=Point3d(x=-18.292682647705078, y=33.780487060546875, z=25.85365867614746),
        acc=Point3d(x=0.6474609375, y=0.301513671875, z=0.786376953125),
        mag=Point3d(x=0.0, y=0.0, z=-0.0),
        raw_pose=Point4d(w=0.9500142931938171, x=0.1318855732679367, y=-0.2588249146938324, z=-0.09857095777988434),
        current_pose=Point4d(w=0.9500142931938171, x=0.1318855732679367, y=-0.2588249146938324, z=-0.09857095777988434),
        euler=Euler3d(roll=0.34807541966438293, pitch=0.48450973629951477, yaw=0.2931704521179199),
        linacc=Point3d(x=0.1816863715648651, y=-9.79304313659668e-05, z=-0.03810983896255493),
        peak=False,
        peak_norm_velocity=0.0,
        timestamp_us=7032570,
    ),
    ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.DOWN),
]
