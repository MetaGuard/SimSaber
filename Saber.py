from SaberMovementData import SaberMovementData
from Bsor import VRObject
from geometry import Vector3, Quaternion

class Saber():
    saber_type: int
    time: float
    movement_data: SaberMovementData

    @property
    def blade_speed(self):
        return self.movement_data.blade_speed

    def __init__(self, saber_type: int):
        self.saber_type = saber_type
        self.movement_data = SaberMovementData()

    def manual_update(self, object: VRObject, time: float):
        self.time = time
        self.handle_pos = Vector3(object.x, object.y, object.z)
        self.handle_rot = Quaternion(object.x_rot, object.y_rot, object.z_rot, object.w_rot)

        self.saber_blade_top_pos = self.handle_pos + Vector3(0, 0, 1).rotate(self.handle_rot)
        self.saber_blade_bottom_pos = self.handle_pos + Vector3(0, 0, 0).rotate(self.handle_rot)

        self.movement_data.add_new_data(self.saber_blade_top_pos, self.saber_blade_bottom_pos, time)
