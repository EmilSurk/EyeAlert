import cv2
import os
import dlib
from scipy.spatial import distance as dist
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.settings import SettingsWithSidebar
from kivy.config import ConfigParser
import numpy as np
from threading import Thread
import pygame
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    final_path = os.path.join(base_path, relative_path)
    if not os.path.isfile(final_path):
        # If the file is not found in the packaged path, revert to the development path
        final_path = os.path.join(os.path.dirname(__file__), relative_path)
    print(f"Resolved path: {final_path}")  # Diagnostic print
    return final_path



# Initialize Pygame Mixer
pygame.mixer.init()

# Global constants
EAR_THRESHOLD = 0.2
EYE_CLOSED_SECONDS = 10  # Duration for the alarm to be triggered
ALARM_SOUND_PATH = resource_path('/Users/emilsk/Desktop/alarm_sound.mp3')
print(ALARM_SOUND_PATH)

# Initialize dlib's face detector and create the facial landmark predictor
predictor_path = resource_path('shape_predictor_68_face_landmarks.dat')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


class VideoStreamWidget(KivyImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.EAR_THRESHOLD = App.get_running_app().config.getfloat('drowsinesssettings', 'EAR_THRESHOLD')
        self.EYE_CLOSED_SECONDS = App.get_running_app().config.getint('drowsinesssettings', 'EYE_CLOSED_SECONDS')
        self.ALARM_VOLUME = App.get_running_app().config.getfloat('drowsinesssettings', 'ALARM_VOLUME')

        self.camera_index = 1  # Starting with camera index 1
        self.init_camera(self.camera_index)
        self.alarm_playing = False
        self.eye_closed_start_time = None
        Clock.schedule_interval(self.update, 1/30)
        self.update_settings()

    def update_settings(self):
        # Accessing the config from the running app instance
        app_config = App.get_running_app().config
        self.ear_threshold = max(0.1, min(float(app_config.get('drowsinesssettings', 'EAR_THRESHOLD')), 0.5))
        self.eye_closed_seconds = max(5, min(int(app_config.get('drowsinesssettings', 'EYE_CLOSED_SECONDS')), 30))
        self.alarm_volume = max(0, min(float(app_config.get('drowsinesssettings', 'ALARM_VOLUME')), 1))
        # Adjust the volume of the alarm
        pygame.mixer.music.set_volume(self.alarm_volume)

    def init_camera(self, camera_index):
        # Release the current camera if it's already initialized
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()

        # Initialize the new camera
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            print(f"Failed to open camera with index {camera_index}")
            return False
        return True

    def play_alarm(self):
        pygame.mixer.music.load(ALARM_SOUND_PATH)
        pygame.mixer.music.set_volume(self.ALARM_VOLUME)
        pygame.mixer.music.play(-1)

    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_playing = False

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            print("Failed to read frame from camera.")
            return  # Skip the rest of the processing for this frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0)

        # Flag to indicate that eyes were detected
        eyes_detected = False

        for face in faces:
            shape = predictor(gray, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
            leftEye = landmarks[36:42]
            rightEye = landmarks[42:48]

            # Draw rectangles around each eye
            self.draw_eye(frame, leftEye)
            self.draw_eye(frame, rightEye)

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            # Check if EAR is below the threshold (eyes closed)
            if ear < self.ear_threshold:  # Use the clamped setting value
                if self.eye_closed_start_time is None:
                    # Record the start time of the eye closure
                    self.eye_closed_start_time = time.time()
                else:
                    # Check how long the eyes have been closed
                    duration_closed = time.time() - self.eye_closed_start_time
                    if duration_closed >= self.eye_closed_seconds:  # Use the clamped setting value
                        # Trigger the alarm if not already playing
                        if not self.alarm_playing:
                            print("Drowsiness detected! Alarm triggered.")
                            self.play_alarm()
                            self.alarm_playing = True
            else:
                # Reset the eye closure timer and stop alarm if eyes are open
                self.eye_closed_start_time = None
                if self.alarm_playing:
                    self.stop_alarm()


            eyes_detected = True  # Set the flag to True as eyes are detected

        if not eyes_detected:
            # If no faces or eyes are detected, display the message
            self.display_message(frame, "Eyes not detected", (0, 0, 255))

        # Convert the frame to texture
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = texture

    def display_message(self, frame, text, color):
        # Get the width and height of the frame
        (h, w) = frame.shape[:2]

        # Set the font scale and thickness
        font_scale = 3  # Increase the scale to make text bigger
        thickness = 5  # Increase the thickness of the text for better visibility

        # Get the text size (width and height) based on the font scale and thickness
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        # Calculate the x, y coordinates of the text to center it
        x = (w - text_width) // 2
        y = (h + text_height) // 2

        # Use cv2.putText() method to put text on the frame
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    def on_stop(self):
        Clock.unschedule(self.update)
        self.capture.release()
        if self.alarm_playing:
            self.stop_alarm()

    def change_camera(self, new_camera_index):
        # Wait until the current frame is processed
        Clock.unschedule(self.update)

        if self.init_camera(new_camera_index):
            self.camera_index = new_camera_index
            print(f"Switched to camera {self.camera_index}")
            Clock.schedule_interval(self.update, 1 / 30)
        else:
            # Reschedule the update with the old camera
            Clock.schedule_interval(self.update, 1 / 30)

    def draw_eye(self, frame, eye):
        (x, y, w, h) = cv2.boundingRect(np.array([eye]))

        # Enlarge the rectangle
        margin = 10  # Margin to add to the rectangle size
        cv2.rectangle(frame, (x - margin, y - margin), (x + w + margin, y + h + margin), (0, 255, 0), 2)

        ear = self.eye_aspect_ratio(eye)
        eye_state = "Open" if ear > EAR_THRESHOLD else "Closed"

        # Increase the text size
        font_scale = 0.7
        text_position = (x - margin, y + h + margin + 20)  # Adjust position based on new rectangle size
        cv2.putText(frame, eye_state, text_position, cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, (0, 255, 0), 2, cv2.LINE_AA)

    def eye_aspect_ratio(self, eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # Compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        return ear

    def on_stop(self):
        self.capture.release()
        if self.alarm_playing:
            self.stop_alarm()

class DrowsinessApp(App):

    def build_config(self, config):
        config.setdefaults('drowsinesssettings', {
            'EAR_THRESHOLD': 0.2,
            'EYE_CLOSED_SECONDS': 10,
            'ALARM_VOLUME': 1.0
        })

    def build_settings(self, settings):
        settings.add_json_panel('Drowsiness Detection Settings',
                                self.config,
                                data="""
                                [
                                    {"type": "numeric", "title": "EAR Threshold", "desc": "EAR Threshold for drowsiness detection", "section": "drowsinesssettings", "key": "EAR_THRESHOLD"},
                                    {"type": "numeric", "title": "Eye Closed Duration", "desc": "Duration (in seconds) for eye closure to trigger alarm", "section": "drowsinesssettings", "key": "EYE_CLOSED_SECONDS"},
                                    {"type": "numeric", "title": "Alarm Volume", "desc": "Volume of the alarm", "section": "drowsinesssettings", "key": "ALARM_VOLUME"}
                                ]
                                """)

    def on_config_change(self, config, section, key, value):
        if section == 'drowsiness_settings':
            if key == 'EAR_THRESHOLD':
                self.video_stream.EAR_THRESHOLD = float(value)
            elif key == 'EYE_CLOSED_SECONDS':
                self.video_stream.EYE_CLOSED_SECONDS = int(value)
            elif key == 'ALARM_VOLUME':
                self.video_stream.ALARM_VOLUME = float(value)

    def build(self):
        self.config = ConfigParser()
        self.build_config(self.config)
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False

        layout = BoxLayout(orientation='vertical')
        self.video_stream = VideoStreamWidget(size_hint=(1, 0.8))
        layout.add_widget(self.video_stream)

        start_button = Button(text="Start", size_hint=(1, 0.1))
        layout.add_widget(start_button)

        stop_button = Button(text="Stop", size_hint=(1, 0.1))
        stop_button.bind(on_press=self.stop_stream)
        layout.add_widget(stop_button)

        # Add a button to change the camera
        change_camera_button = Button(text="Change Camera", size_hint=(1, 0.1))
        change_camera_button.bind(on_press=self.change_camera)
        layout.add_widget(change_camera_button)

        settings_button = Button(text="Settings", size_hint=(1, 0.1))
        settings_button.bind(on_press=self.open_settings)
        layout.add_widget(settings_button)

        return layout

    def open_settings_panel(self, instance):
        self.open_settings()

    def stop_stream(self, instance):
        self.video_stream.on_stop()
        App.get_running_app().stop()  # Add this line to close the application

    def change_camera(self, instance):
        # Here you can cycle through camera indices or prompt the user for an index
        new_camera_index = (self.video_stream.camera_index + 1) % 2  # Toggling between 0 and 1 for example
        self.video_stream.change_camera(new_camera_index)

    def on_config_change(self, config, section, key, value):
        if section == 'drowsinesssettings':
            self.video_stream.update_settings()

if __name__ == '__main__':
    DrowsinessApp().run()
