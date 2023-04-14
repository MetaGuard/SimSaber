from Geometry import Vector3, Quaternion, Orientation, RAD_TO_DEG

quat1 = Quaternion.from_Euler(319.45770, 295.00520, 10.19963);
print(Quaternion(-0.335855700, -0.476015200, -0.115075900, 0.804591800));
print(quat1, "\n");

eul1 = quat1.to_Euler();
print(Vector3(319.45770, 295.00520, 10.19963))
print(eul1, "\n");

quat2 = Quaternion.from_forward_and_up(
    Vector3(0.28664306476712226, -0.17795072543565926, 2.761551596672372),
    Vector3(-0.005308421083006178, 0.9997270086669968, -0.02275365481287681)
)
print(Quaternion(0.03203, 0.05162, -0.00019, 0.99815));
print(quat2, "\n");
