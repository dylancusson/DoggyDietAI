from picamera2 import Picamera2
import cv2
import numpy as np
import time
import datetime

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# Log file setup
log_filename = "kibble_log.txt"
with open(log_filename, "a") as log_file:
    log_file.write("\n--- New Session Started ---\n")

# Capture an initial baseline frame
time.sleep(2)  # Allow camera to adjust
baseline_frame = picam2.capture_array()
baseline_frame = cv2.cvtColor(baseline_frame, cv2.COLOR_RGB2BGR)

# **Crop the image** (Keep only the first 215 pixels in height)
baseline_frame = baseline_frame[0:215, :]

# Convert baseline to grayscale
gray_baseline = cv2.cvtColor(baseline_frame, cv2.COLOR_BGR2GRAY)
blurred_baseline = cv2.GaussianBlur(gray_baseline, (5, 5), 0)

# Adaptive thresholding
baseline_thresh = cv2.adaptiveThreshold(
    blurred_baseline, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
)

# Morphological operations
kernel = np.ones((3, 3), np.uint8)
baseline_thresh = cv2.morphologyEx(baseline_thresh, cv2.MORPH_OPEN, kernel)

# Detect initial kibble count
baseline_contours, _ = cv2.findContours(baseline_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
baseline_contours = [c for c in baseline_contours if cv2.contourArea(c) > 50]
baseline_kibble_count = len(baseline_contours)

print(f"Baseline kibble count: {baseline_kibble_count}")

# Initialize background subtractor for motion detection
fgbg = cv2.createBackgroundSubtractorMOG2()
last_detection_time = time.time()

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # **Crop the frame to match the tracking area**
    frame = frame[0:215, :]

    # Motion detection
    fgmask = fgbg.apply(frame)
    motion_level = np.sum(fgmask) / fgmask.size

    if motion_level > 10:
        last_detection_time = time.time()

        # Convert frame to grayscale and apply threshold
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Find contours (kibble pieces)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if 50 < cv2.contourArea(c) < 500]
        kibble_count = len(contours)

        # Draw bounding boxes on detected kibble
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display kibble count
        cv2.putText(frame, f"Kibble Count: {kibble_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA)

        # Compare with baseline count
        pieces_eaten = baseline_kibble_count - kibble_count
        if pieces_eaten > 0:
            print(f"{pieces_eaten} pieces eaten!")

            # Log data to file
            with open(log_filename, "a") as log_file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp} - Kibble Count: {kibble_count}, Pieces Eaten: {pieces_eaten}\n")

        # Overlay the processed threshold image for debugging
        overlay = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)  # Convert to BGR for overlay
        combined = np.hstack((frame, overlay))  # Side-by-side view

    else:
        combined = frame  # No motion, just show regular feed

    # Show the camera feed with overlay
    cv2.imshow("Dog Food Tracker - Cropped", combined)

    # If no motion for 10 seconds, reset the counter
    if time.time() - last_detection_time > 10:
        baseline_kibble_count = kibble_count  # Update baseline when idle

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
