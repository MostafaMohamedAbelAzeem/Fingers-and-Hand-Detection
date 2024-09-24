                                        #import important libraries
import cv2              #for openCv
import mediapipe as mp  #for hand-tracking and we named it mp instead of mediapipe for ease
#import serial           #for serial communication with arduino

#----------------------------------------------------------------------------------------------------------------------------------

#arduino = serial.Serial('COM3', 9600)  #Establish serial communication with arduino using port COM3 and at baud rate 9600 


cap = cv2.VideoCapture(0)     #Create vedio capture from webCam
mpHands = mp.solutions.hands  #Initialize the MediaPipe Hands module for hand-tracking.
hands = mpHands.Hands()       #Create an instance of the Hands class responsible for detecting and tracking hand landmarks using the MediaPipe library.
mpDraw = mp.solutions.drawing_utils  #Import the drawing utilities from MediaPipe for visualizing the hand landmarks.

                                      #Define the finger coordinates and thumb coordinates for finger counting.
fingerCoordinates = [(8, 6), (12, 10), (16, 14), (20, 18)]  
thumbCoordinates = (4, 2)

#---------------------------------------------------------------------------------------------------------------------------------
                                              #Infinite loop to continously send the frames 
while True:

    good, image = cap.read() #Read a frame from the video capture object.
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  #Convert the frame from BGR to RGB color space because MediaPipe's hand tracking algorithm is designed to work with RGB images.
    result = hands.process(imageRGB) #Process the RGB image using the Hands module to detect hand landmarks.
    multi_marks = result.multi_hand_landmarks #Retrieve the multi-hand landmarks from the result.

                                           #If hand landmarks are detected, iterate over each detected hand.
    if multi_marks:   
        handPoints = []
                                           #Draw the hand landmarks and connections on the image using the drawing utilities.
        for handLms in multi_marks:
            mpDraw.draw_landmarks(image, handLms, mpHands.HAND_CONNECTIONS,
                                  landmark_drawing_spec=mpDraw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                                  connection_drawing_spec=mpDraw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2))
                                           #Extract the x and y coordinates of each hand landmark and store them in handPoints.
            for ind, lm in enumerate(handLms.landmark):
                h, w, c = image.shape  #retrieves the height (h), width (w), and number of channels (c) of the image.
                cx, cy = int(lm.x * w), int(lm.y * h) #calculates the pixel coordinates (cx, cy) of the current hand landmark by scaling the normalized landmark coordinates (lm.x, lm.y) with the image dimensions.
                handPoints.append((cx, cy)) #adds the calculated (x, y) coordinates of the hand landmark to the handPoints list.
                                           
                                           
                                           #Draw filled circles on the image at the detected hand landmark positions.
        for points in handPoints:
            cv2.circle(image, points, 10, (255, 0, 0), cv2.FILLED)
        
        UpFingers = 0 #intialize number of fingers up as 0 to count the number of fingers extended.

                                     #Iterate over the finger coordinates and check if the y-coordinate of the first point is less than the y-coordinate of the second point. If true, increment UpFingers.
        for coordinate in fingerCoordinates:
            if handPoints[coordinate[0]][1] < handPoints[coordinate[1]][1]:
                UpFingers += 1
                                     
                                #Special case for thumb : Check if the x-coordinate of the first thumb point is greater than the x-coordinate of the second thumb point. If true, increment UpFingers.     
        if handPoints[thumbCoordinates[0]][0] > handPoints[thumbCoordinates[1]][0]:
            UpFingers += 1
 
                                   #Send the finger count to the Arduino by writing it as a string over the serial connection.
        #arduino.write(str(UpFingers).encode())

                                   #Draw the finger count on the image.
        cv2.putText(image, str(UpFingers), (150, 150), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.0, (255, 0, 0), 2)
                                   #Display the image with the finger count.
    cv2.imshow("Finger Count", image)
                                   #If the 'q' key is pressed, break the loop and exit the program.
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

#arduino.close()#Close the serial connection with the Arduino.
cap.release() #Release the video capture object.
cv2.destroyAllWindows()#Close all OpenCV windows.
