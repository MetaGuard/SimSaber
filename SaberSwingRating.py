class SaberSwingRating:
    k_max_normal_angle_diff = 90.0
    k_tolerance_normal_angle_diff = 75.0
    k_max_before_cut_swing_duration = 0.4
    k_max_after_cut_swing_duration = 0.4
    k_before_cut_angle_for_1_rating = 100.0
    k_after_cut_angle_for_1_rating = 60.0

    @staticmethod
    def normal_rating(normal_diff):
        return 1.0 - min(max((normal_diff - 75.0) / 15.0, 0.0), 1.0)

    @staticmethod
    def before_cut_step_rating(angle_diff, normal_diff):
        return angle_diff * SaberSwingRating.normal_rating(normal_diff) / 100.0

    @staticmethod
    def after_cut_step_rating(angle_diff, normal_diff):
        return angle_diff * SaberSwingRating.normal_rating(normal_diff) / 60.0