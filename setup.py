from setuptools import setup

APP = ['main.py']
DATA_FILES = ['resources/alarm_sound.mp3', 'dlib-models/shape_predictor_68_face_landmarks.dat']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['cv2', 'dlib', 'scipy', 'kivy', 'pygame'],
    'includes': ['kivy'],  # Explicitly include kivy
    'resources': DATA_FILES,
}


setup(
    app=APP,
    name="DrowsinessApp",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)