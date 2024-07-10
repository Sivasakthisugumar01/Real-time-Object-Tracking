import cv2
import serial
import time

# Initialize serial communication with Arduino
ser = serial.Serial('COM6', 9600, timeout=1)  # Replace 'COM6' with your Arduino port
time.sleep(2)  # Wait for the serial connection to initialize

# Initialize the webcam
cap = cv2.VideoCapture(1)

# Define frame dimensions
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
center_x = frame_width / 2
center_y = frame_height / 2

# Servo angles
pan_angle = 90
tilt_angle = 90

# Variable to store selected object's bounding box
bbox = None

def map_value(value, left_min, left_max, right_min, right_max):
    # Maps a value from one range to another
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = float(value - left_min) / float(left_span)
    return right_min + (value_scaled * right_span)

def select_object(event, x, y, flags, param):
    global bbox
    if event == cv2.EVENT_LBUTTONDOWN:
        bbox = (x, y, 0, 0)  # Initialize bounding box with initial click coordinates

# Create a named window
cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback('Frame', select_object)

# Initial phase to capture image and select an object
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display the frame and wait for the user to select an object
    cv2.imshow('Frame', frame)

    if bbox is not None:
        x, y, w, h = cv2.selectROI('Frame', frame, fromCenter=False, showCrosshair=True)
        bbox = (x, y, w, h)
        break

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Initialize object tracker
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# Tracking phase
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update the tracker and get the new bounding box
    success, bbox = tracker.update(frame)
    if success:
        x, y, w, h = [int(v) for v in bbox]
        object_center_x = x + w / 2
        object_center_y = y + h / 2

        # Calculate error between object center and frame center
        error_x = object_center_x - center_x
        error_y = object_center_y - center_y

        # Map error to servo angle adjustments
        pan_angle -= map_value(error_x, -center_x, center_x, -5, 5)
        tilt_angle += map_value(error_y, -center_y, center_y, -5, 5)

        # Limit the angles to the range 0-180
        pan_angle = max(0, min(180, pan_angle))
        tilt_angle = max(0, min(180, tilt_angle))

        # Send the servo angles to Arduino
        ser.write(f'{int(pan_angle)},{int(tilt_angle)}\n'.encode())

        # Draw bounding box around the object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the resulting frame in full screen
    cv2.imshow('Frame', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
ser.close()
