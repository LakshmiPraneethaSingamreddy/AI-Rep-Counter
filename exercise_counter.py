# # import math

# # class ExerciseCounter:
# #     def __init__(self, joint_indices=(11, 13, 15), angle_range=(30, 160)):
# #         self.joint_indices = joint_indices
# #         self.angle_range = angle_range
# #         self.counter = 0
# #         self.stage = None

# #     def calculate_angle(self, a, b, c):
# #         ab = [b.x - a.x, b.y - a.y]
# #         cb = [b.x - c.x, b.y - c.y]
# #         dot = ab[0] * cb[0] + ab[1] * cb[1]
# #         mag_ab = math.hypot(*ab)
# #         mag_cb = math.hypot(*cb)
# #         angle = math.acos(dot / (mag_ab * mag_cb))
# #         return math.degrees(angle)

# #     def update(self, landmarks):
# #         a, b, c = (landmarks[i] for i in self.joint_indices)
# #         angle = self.calculate_angle(a, b, c)

# #         if angle > self.angle_range[1]:
# #             self.stage = "down"
# #         if angle < self.angle_range[0] and self.stage == "down":
# #             self.stage = "up"
# #             self.counter += 1

# #         return angle, self.counter, self.stage


# import cv2
# import mediapipe as mp
# import numpy as np

# class ExerciseCounter:
#     def __init__(self, joint_indices, angle_range):
#         self.joint_indices = joint_indices if isinstance(joint_indices[0], tuple) else [joint_indices]
#         self.angle_range = angle_range
#         self.counter = 0
#         self.stage = {}
#         for idx in range(len(self.joint_indices)):
#             self.stage[idx] = None

#     def calculate_angle(self, a, b, c):
#         a = np.array(a)
#         b = np.array(b)
#         c = np.array(c)

#         ba = a - b
#         bc = c - b

#         cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#         angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
#         return np.degrees(angle)

#     def update(self, landmarks):
#         counted = False
#         display_angle = 0

#         for idx, (a, b, c) in enumerate(self.joint_indices):
#             try:
#                 point_a = [landmarks[a].x, landmarks[a].y]
#                 point_b = [landmarks[b].x, landmarks[b].y]
#                 point_c = [landmarks[c].x, landmarks[c].y]
#                 angle = self.calculate_angle(point_a, point_b, point_c)

#                 if idx == 0:
#                     display_angle = angle  # prioritize showing left angle

#                 if angle > self.angle_range[1]:
#                     self.stage[idx] = "down"
#                 if angle < self.angle_range[0] and self.stage[idx] == "down":
#                     self.stage[idx] = "up"
#                     self.counter += 1
#                     counted = True


#             except:
#                 continue

#         return display_angle, self.counter, self.stage


import math

class ExerciseCounter:
    def __init__(self, joint_indices, angle_range=(30, 160)):
        self.joint_indices = joint_indices  # List of (a, b, c) tuples for both sides
        self.min_angle, self.max_angle = angle_range
        self.stage = {f"side{idx}": None for idx in range(len(joint_indices))}
        self.counter = 0

    def calculate_angle(self, a, b, c):
        a = [a.x, a.y]
        b = [b.x, b.y]
        c = [c.x, c.y]

        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]

        dot_product = ba[0]*bc[0] + ba[1]*bc[1]
        magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)

        cosine_angle = dot_product / (magnitude_ba * magnitude_bc + 1e-7)
        angle = math.degrees(math.acos(min(1.0, max(-1.0, cosine_angle))))
        return angle

    def update(self, landmarks):
        angles = []
        both_up = True
        both_down = True

        for idx, (a, b, c) in enumerate(self.joint_indices):
            angle = self.calculate_angle(landmarks[a], landmarks[b], landmarks[c])
            angles.append(angle)
            side_key = f"side{idx}"

            if angle > self.max_angle:
                self.stage[side_key] = "down"
            elif angle < self.min_angle and self.stage[side_key] == "down":
                self.stage[side_key] = "up"

            # Check global stage condition
            if self.stage[side_key] != "up":
                both_up = False
            if self.stage[side_key] != "down":
                both_down = False

        # If all sides were "up" together just now, count as one rep
        if both_up and self.prev_stage == "down":
            self.counter += 1
            self.prev_stage = "up"
        elif both_down:
            self.prev_stage = "down"

        return sum(angles) / len(angles), self.counter, self.prev_stage
