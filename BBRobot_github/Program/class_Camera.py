from picamera2 import Picamera2
import cv2
import numpy as np
import threading
lock = threading.Lock()


class Camera:
    def __init__(self):
        # Initialize and set up the camera
        self.picam2 = Picamera2()
        self.height = 480
        self.width = 480
        self.config = self.picam2.create_video_configuration(
            main={"format": 'XRGB8888', "size": (self.height, self.width)},
            controls={
                "FrameDurationLimits": (8333, 8333),
                "ExposureTime": 8000
            }
        )
        self.picam2.configure(self.config)

        # Define the HSV range for fluorescent pink
        self.lower_pink = np.array([140, 150, 50])  # H: approximately 140 degrees to
        self.upper_pink = np.array([180, 255, 255])  # H: approximately 170 degrees to
        # Start the camera
        self.picam2.start()

    def take_pic(self):
        image = self.picam2.capture_array()
        return image

    def show_video(self, image):
        cv2.imshow("Live", image)
        cv2.waitKey(1)

    def find_ball(self, image):
        # Convert to HSV color space
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Create a mask based on the color range
        mask = cv2.inRange(image_hsv, self.lower_pink, self.upper_pink)
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            # Get the minimum enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            area = cv2.contourArea(largest_contour)  # Calculate the area
            if area > 200:  # Ignore noise with a threshold value
                # Draw a circle on the image
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                self.show_video(image)
                d = radius*2
                h = 10000/d
                # Correct the center
                x -= self.height / 2
                y -= self.width / 2
                x, y = -y, x
                return int(x), int(y), int(area)  # Return the image and coordinates, area
        self.show_video(image)
        return -1, -1, 0  # Return when no ball is detected

    def clean_up_cam(self):
        self.picam2.stop()
        self.picam2.close()
        cv2.destroyAllWindows()
		