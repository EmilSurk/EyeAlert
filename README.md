# EyeAlert

EyeAlert is an innovative application designed to assist college students who unintentionally fall asleep during exams or study sessions. Leveraging advanced eye-detection algorithms, EyeAlert monitors the user's eyes and triggers an alarm if it detects that they have fallen asleep. This project aims to help students maintain alertness and improve their academic performance.

## Eye State Representation

<p float="left">
  <img src="EyeAlert-Closed.jpg" width="400" />
  <img src="EyeAlert-Open.jpg" width="400" /> 
</p>

## Features

- **Eye-Detection**: Utilizes computer vision techniques to monitor the user's eyes in real-time.
- **Drowsiness Alarm**: An alarm is triggered if the user's eyes close for a certain threshold duration, indicating potential drowsiness or sleep.
- **Customizable Settings**: Users can adjust the Eye Aspect Ratio (EAR) threshold, the duration before the alarm is triggered, and the alarm volume.
- **Obstacle Handling**: Incorporates the ability to add obstacles, simulating real-world situations where the line of sight to the user's eyes may be temporarily obstructed.

## Goal

The goal of EyeAlert is to provide students with a tool that promotes active engagement and alertness during critical tasks such as exams or intensive study sessions. By preventing unintended sleep, students can maintain focus, which is essential for academic success.

## Getting Started

To get started with EyeAlert, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/EmilSurk/EyeAlert
    ```
2. Ensure Python is installed on your system.
3. Install Dependencies:
    ```
    pip install opencv-python dlib scipy kivy numpy pygame
    ```
4. Run the Application:
    ```
    python3 EyeAlert/main.py
    ```

Make sure you have a webcam connected to your computer as the application relies on real-time video feed.

## Usage

Once the application is running, position yourself so that your face is clearly visible to the webcam. Adjust the EAR threshold and eye-closed duration to suit your preference and the lighting conditions. Start the monitoring process and focus on your task; EyeAlert will alert you if it detects that you've fallen asleep.

## Contributing

Contributions to EyeAlert are welcome! If you have suggestions for improvements or want to contribute to the code, please feel free to create an issue or submit a pull request.

## License

EyeAlert is open-source software licensed under the MIT license.
