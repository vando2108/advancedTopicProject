import numpy as np
import cv2
from collections import deque
import pyautogui
import time
import os
import math

#Get screen resolution
os.system('python3 get_screen_resolution.py')
FILE = open('screen_resolution.txt', 'r')
width_screen, height_screen = list(map(int, FILE.readline().split(' ')))

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.00

class Mouse:
    def __init__(self):
        self.MOUSE_ENABLE = False
        self.x, self.y = pyautogui.position()
        pyautogui.move(-self.x, -self.y)
        pyautogui.move(width_screen / 2, height_screen / 2)
        self.x, self.y = 0, 0
        pass

    def move(self, x, y):
        pyautogui.move(x, y)
        pass

    def moveTo(self, x, y):
        pyautogui.moveTo(x, y)
        pass

    def getPosition(self):
        return self.x, self.y
        pass

    def clickLeft(self, x, y):
        pyautogui.click(x=x, y=y, button='left')
        pass

    def clickRight(self, x, y):
        pyautogui.click(x=x, y=y, button='right')
        pass

    def scrollVertical(self, y):
        pyautogui.vscroll(y)
        pass

    def scrollHorizontal(self, x):
        pyautogui.hscroll(x)
        pass
        

mouse = Mouse()

# Note: color coding is in HSV, not RGB !
# Define the upper and lower boundaries for a color to be considered "Blue"
blueLower = np.array([100, 100, 100])
blueUpper = np.array([140, 255, 255])

# Define the upper and lower boundaries for a color to be considered "Red"
redLower = np.array([150, 150, 150])
redUpper = np.array([180, 255, 255])

# Define a 5x5 kernel for erosion and dilation
kernel = np.ones((5, 5), np.uint8)

# Setup deques to store separate colors in separate arrays
bpoints = [deque(maxlen=512)]

bindex = 0

colors = [(255, 0, 0)]
colorIndex = 0

# Setup the Paint interface
paintWindow = np.zeros((471, 636, 3)) + 255       
paintWindow = cv2.rectangle(paintWindow, (40,1), (140,65), (0,0,0), 2)
cv2.putText(paintWindow, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

# Load the video
camera = cv2.VideoCapture(0)    

detected = []
Position = []

# Keep looping
while True:
    time.sleep(1/65)
    # Grab the current paintWindow
    (grabbed, frame) = camera.read()

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Add the coloring options to the frame
    frame = cv2.rectangle(frame, (40, 1), (140, 65), (122, 122, 122), -1)
    cv2.putText(frame, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    if mouse.MOUSE_ENABLE == False:
        cv2.circle(frame, (318, 235), 15, (0, 255, 0), thickness=2)
        cv2.putText(frame, "MOVE YOUR FINGER HERE TO CONTROL THE MOUSE", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 255, 255), 2, cv2.LINE_AA)
        pass

    # Check to see if we have reached the end of the video
    if not grabbed:
        break

    # Determine which pixels fall within the _blue_ boundaries and then blur the binary image
    blueMask = cv2.inRange(hsv, blueLower, blueUpper)
    blueMask = cv2.erode(blueMask, kernel, iterations=2)
    blueMask = cv2.morphologyEx(blueMask, cv2.MORPH_OPEN, kernel)
    blueMask = cv2.dilate(blueMask, kernel, iterations=1)

    # Determine which pixels fall within the _red_ boundaries and then blur the binary image
    redMask = cv2.inRange(hsv, redLower, redUpper)
    redMask = cv2.erode(redMask, kernel, iterations=2)
    redMask = cv2.morphologyEx(redMask, cv2.MORPH_OPEN, kernel)
    redMask = cv2.dilate(redMask, kernel, iterations=1)

    # Find contours of the blue objects in the image
    (blueCnts, _) = cv2.findContours(blueMask.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)

    # Find contours of the red objects in the image
    (redCnts, _) = cv2.findContours(redMask.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    center = None

    haveAction = False

    # Check to see if any blue contours were found
    if len(blueCnts) > 0:
        haveAction = True

    	# Sort the blue contours and find the largest one -- we
    	# will assume this contour correspondes to the area of the bottle cap
        blueCnt = sorted(blueCnts, key = cv2.contourArea, reverse = True)[0]
        # Get the radius of the enclosing circle around the found contour
        ((xb, yb), radius_b) = cv2.minEnclosingCircle(blueCnt)

        # Check if the object is in the middle of the camera frame
        if math.sqrt((xb - 318)**2 + (yb - 235)**2) < 10:
            mouse.MOUSE_ENABLE = True
            mouse.moveTo(width_screen / 2, height_screen / 2)
            pass

        # If in the last turn we deteced action, we will move cursor
        if len(detected) != 0 and detected[-1] == True and mouse.MOUSE_ENABLE:
            tempx, tempy = Position[-1]
            mouse.move(xb*4.0 - tempx*4.0, yb*4.0 - tempy*4.0)
            pass    

        # If the red object appear, we will click the left mouse
        if len(redCnts) > 0 and mouse.MOUSE_ENABLE:
            # Sort the red contours and find the largest one -- we
            redCnt = sorted(redCnts, key = cv2.contourArea, reverse = True)[0]
            # Get the radius of the enclosing circle around the found contour
            ((xr, yr), radius_r) = cv2.minEnclosingCircle(redCnt)
            # Draw the circle around the red contour
            cv2.circle(frame, (int(xr), int(yr)), int(radius_r), (255, 255, 0), 2)
            mouse.clickLeft(xb, yb)
            pass

        # Draw the circle around the blue contour
        cv2.circle(frame, (int(xb), int(yb)), int(radius_b), (0, 255, 255), 2)

        # Get the moments to calculate the center of the contour (in this case Circle)
        M = cv2.moments(blueCnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 65:
            if 40 <= center[0] <= 140: # Clear All
                bpoints = [deque(maxlen=512)]

                bindex = 0

                paintWindow[67:,:,:] = 255
            elif 160 <= center[0] <= 255:
                    colorIndex = 0 # Blue
        else :
            if colorIndex == 0:
                bpoints[bindex].appendleft(center)
        Position.append((int(xb), int(yb)))
    # Append the next deque when no contours are detected (i.e., bottle cap reversed)
    else:
        bpoints.append(deque(maxlen=512))
        bindex += 1
        mouse.MOUSE_ENABLE = False
        pass
    
    detected.append(haveAction)

    # Draw lines of all the colors (Blue, Green, Red and Yellow)
    points = [bpoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)
    # Show the frame and the paintWindow image

    cv2.imshow("Tracking", frame)
    cv2.imshow("Paint", paintWindow)

	# If the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()