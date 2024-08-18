import random
import cv2
import cvzone
import mediapipe as mp
import time

# Initialize Mediapipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [Player, AI]
playerMove = None
imgAI = None  # Placeholder for the AI's move image

while True:
    success, img = cap.read()

    # Ensure the frame was successfully captured before proceeding
    if not success:
        print("Failed to capture frame")
        continue  # Retry until frame is successfully captured

    # Flip the image and convert it to RGB for Mediapipe
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image with Mediapipe
    results = hands.process(img_rgb)
    cursors = []

    # Extract hand landmarks if available
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = [(int(lm.x * img.shape[1]), int(lm.y * img.shape[0])) for lm in hand_landmarks.landmark]
            cursors.append(lmList[8])  # Get the index finger tip position

            # Draw hand landmarks on the image
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detecting hand gesture (Rock, Paper, Scissors)
            if len(lmList) != 0:
                # Assume a basic decision-making process based on the cursor position
                # Rock detection: When all fingers are folded (i.e., distances between knuckles and tips are small)
                if lmList[8][1] > lmList[6][1] and lmList[12][1] > lmList[10][1] and \
                        lmList[16][1] > lmList[14][1] and lmList[20][1] > lmList[18][1]:
                    playerMove = 1  # Rock
                # Paper detection: When all fingers are extended
                elif lmList[8][1] < lmList[6][1] and lmList[12][1] < lmList[10][1] and \
                        lmList[16][1] < lmList[14][1] and lmList[20][1] < lmList[18][1]:
                    playerMove = 2  # Paper
                # Scissors detection: When index and middle fingers are extended, but ring and pinky are folded
                elif lmList[8][1] < lmList[6][1] and lmList[12][1] < lmList[10][1] and \
                        lmList[16][1] > lmList[14][1] and lmList[20][1] > lmList[18][1]:
                    playerMove = 3  # Scissors

    # Read the background image
    imgBG = cv2.imread("Resources/BG.png")

    # Resize the captured frame to fit into the target region (420x400)
    img_resized = cv2.resize(img, (400, 420))

    # If the game has started, run the game logic
    if startGame:
        if not stateResult:
            # Start the timer
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

                if cursors:  # Check if any hand landmarks are detected
                    if playerMove is not None:
                        # AI makes a random move
                        randomNumber = random.randint(1, 3)
                        imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)
                        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                        # Determine the winner (corrected scoring logic)
                        if (playerMove == 1 and randomNumber == 3) or \
                                (playerMove == 2 and randomNumber == 1) or \
                                (playerMove == 3 and randomNumber == 2):
                            scores[0] += 1  # Player wins
                        elif (playerMove == 3 and randomNumber == 1) or \
                                (playerMove == 1 and randomNumber == 2) or \
                                (playerMove == 2 and randomNumber == 3):
                            scores[1] += 1  # AI wins

    # Overlay the resized image into the background
    imgBG[234:654, 795:1195] = img_resized

    # Display the scores
    cv2.putText(imgBG, str(scores[1]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[0]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Display the final result (the AI's move will stay on the screen)
    if imgAI is not None:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    cv2.imshow("BG", imgBG)

    # Wait for 's' key to start a new game
    key = cv2.waitKey(1)
    if key == ord('s'):
        startGame = True
        initialTime = time.time()
        stateResult = False
        playerMove = None
        imgAI = None  # Reset the AI's move image for the next round
        print("Game started!")

    # Press 'q' to quit the game
    if key == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
