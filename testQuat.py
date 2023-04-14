from Geometry import Vector3, Quaternion, Orientation, RAD_TO_DEG

quat1 = Quaternion.from_Euler(319.45770, 295.00520, 10.19963);
print(Quaternion(-0.335855700, -0.476015200, -0.115075900, 0.804591800));
print(quat1, "\n");

eul1 = quat1.to_Euler();
print(Vector3(319.45770, 295.00520, 10.19963))
print(eul1);
