#!usr/bin/python 
import argparse
import datetime
import imutils
import math
import cv2
import numpy as np

#these are the pixel dimensions for the camera
width = 400
height = 400 

#these are the extra off-sets to check how far away from entrance or exit lines
offsetRefLines = 75

#minContour is the minimum threshold that the camera will look for
minContour = 8000 #original was 12000, smaller value means more objects will be picked up


enterCounter = 0
exitCounter = 0

#function to check if an object has entered
def checkIn(y, yEnterLine, yExitLine):
    # how far is the object (y) from the "enter line's y-value"?
    absoluteDistance = abs(y - yEnterLine)
    # if it's less than or equal to 2 and less than the "exit line's y-value", then you've entered
    if ((absoluteDistance <= 2) and (y < yExitLine)):
        return 1
    else:
        return 0


#function to check if an object has exited
def checkOut(y, yEnterLine, yExitLine):
    absoluteDistance = abs(y - yExitLine)
    if ((absoluteDistance <= 2) and (y > yEnterLine)):
        return 1
    else:
        return 0

#camera = cv2.VideoCapture("test2.mp4") #testing using a video file 
camera = cv2.VideoCapture(0)  #testing using a webcam feed 
firstFrame = None

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # initial frame
    frameDelta = cv2.absdiff(firstFrame, gray)

    #check the framedelta feed
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)



    #cnts is the contours which helps detect what is in the frame --> gets passed in the following
    #for loop where the rectangle is then drawn
    _, cnts= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # loop over the contours


    yEnterLine = (height / 3) - offsetRefLines #Line for enter - horizontal 
    yExitLine = (height / 3) + offsetRefLines #Line for exit - horizontal 



    #these two lines only draw the line; does not do anything except to display
    cv2.line(frame, (0, yEnterLine), (width, yEnterLine), (250, 0, 1), 2)
    cv2.line(frame, (0, yExitLine), (width, yExitLine), (0, 0, 225), 2)
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < minContour:   #12000           
            # print("Printing contour area: ")
            # print(str(cv2.contourArea(c)))
            continue
            #break 

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # cv2.line(frame, (width / 2, 0), (width, 450), (250, 0, 1), 2) #blue line OUT
        # cv2.line(frame, (width / 2 - 50, 0), (width - 50, 450), (0, 0, 255), 2)#red line IN


        #this is the X and Y center for each object rectangle 
        rectangleXCentroid = ((x + x + w) / 2)
        rectangleYCentroid = ((y + y + w) / 2)
        rectangleCentroid = (rectangleXCentroid, rectangleYCentroid)

        #the red center of the rectangle 


        cv2.circle(frame, rectangleCentroid, 1, (0, 0, 255), 5) 

        if (checkIn(rectangleYCentroid, yEnterLine, yExitLine)):
            enterCounter += 1
        if (checkOut(rectangleYCentroid, yEnterLine, yExitLine)):
            exitCounter += 1

        # if(testIntersectionIn((x + x + w) / 2, (y + y + h) / 2)):
        #     textIn += 1

        # if(testIntersectionOut((x + x + w) / 2, (y + y + h) / 2)):
        #     textOut += 1

        # draw the text and timestamp on the frame

        # show the frame and record if the user presses a key
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.putText(frame, "In: {}".format(str(enterCounter)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Out: {}".format(str(exitCounter)), (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Security Feed", frame)


# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()