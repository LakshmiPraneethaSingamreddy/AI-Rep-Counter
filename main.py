# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse, RedirectResponse
# import pickle
# import cv2
# import mediapipe as mp
# from exercise_counter import ExerciseCounter

# app = FastAPI()

# @app.get("/")
# def root():
#     return RedirectResponse(url="/ui")

# @app.get("/ui", response_class=FileResponse)
# def serve_ui():
#     return "static/index.html"

# app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/start/{exercise_name}")
# def start_tracking(exercise_name: str):
#     try:
#         with open("exercise_configs.pkl", "rb") as f:
#             configs = pickle.load(f)
#     except FileNotFoundError:
#         return {"error": "Missing config file."}

#     if exercise_name not in configs:
#         return {"error": f"Unknown exercise: {exercise_name}"}

#     config = configs[exercise_name]
#     counter = ExerciseCounter(
#         joint_indices=config["joint_indices"],
#         angle_range=config["angle_range"]
#     )

#     mp_drawing = mp.solutions.drawing_utils
#     mp_pose = mp.solutions.pose

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         return {"error": "Webcam not accessible"}

#     window = f"{config['name']} Tracker"

#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = pose.process(image)
#             image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#             try:
#                 landmarks = results.pose_landmarks.landmark
#                 angle, count, stage = counter.update(landmarks)
#                 joint = landmarks[counter.joint_indices[1]]
#                 coords = (int(joint.x * 640), int(joint.y * 480))
#                 cv2.putText(image, f"Angle: {int(angle)}", coords, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

#                 # Overlay counters
#                 cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
#                 cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
#                 cv2.putText(image, str(count), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
#                 cv2.putText(image, 'STAGE', (65,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
#                 cv2.putText(image, stage, (60,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
#             except:
#                 pass

#             mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#             cv2.imshow(window, image)

#             if cv2.waitKey(10) & 0xFF == ord('q'):
#                 break
#             if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
#                 break

#     cap.release()
#     cv2.destroyAllWindows()
#     return {"exercise": config["name"], "total_reps": counter.counter}


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import pickle
import cv2
import mediapipe as mp
from exercise_counter import ExerciseCounter

app = FastAPI()

# Redirect root to UI
@app.get("/")
def redirect_to_ui():
    return RedirectResponse(url="/ui")

@app.get("/ui", response_class=FileResponse)
def serve_ui():
    return "static/index.html"

app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------- REP COUNTER ENDPOINT ----------------

@app.get("/start/{exercise_name}")
def start_tracking(exercise_name: str):
    try:
        with open("exercise_configs.pkl", "rb") as f:
            configs = pickle.load(f)
    except FileNotFoundError:
        return {"error": "Config file not found."}

    if exercise_name not in configs:
        return {"error": f"Invalid exercise: {exercise_name}"}

    config = configs[exercise_name]
    counter = ExerciseCounter(
        joint_indices=config["joint_indices"],
        angle_range=config["angle_range"]
    )

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"error": "Webcam not accessible."}

    window_name = f"{config['name']} Tracker"

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                angle, count, stage = counter.update(landmarks)

                # Use first joint group for angle display
                joint = landmarks[counter.joint_indices[0][1]]
                coords = tuple((int(joint.x * 640), int(joint.y * 480)))
                cv2.putText(image, f"Angle: {int(angle)}", coords,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # Counter box
                cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
                cv2.putText(image, 'REPS', (15, 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(image, str(count), (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                # cv2.putText(image, 'STAGE', (65, 12),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                # cv2.putText(image, str(stage), (60, 60),
                #             cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

            except Exception as e:
                pass

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.imshow(window_name, image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

    cap.release()
    cv2.destroyAllWindows()

    return {
        "exercise": config["name"],
        "total_reps": counter.counter
    }
