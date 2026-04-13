import cv2
import mediapipe as mp
import numpy as np
import os
import random
import time

print("="*50)
print("   GESTURE TO MEME SYSTEM v2.0")
print("="*50)
print("Loading MediaPipe...")

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # Changed to 2 for multiple hands!
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

print("✓ MediaPipe loaded!")

# Load MULTIPLE memes per gesture
def load_memes():
    memes = {
        "thumbs_up": [],
        "peace": [],
        "pointing": [],
        "open_palm": []
    }
    
    # You can add MULTIPLE images for each gesture!
    # Just name them like: thumbs_up1.jpg, thumbs_up2.jpg, etc.
    
    print("\nLoading meme images...")
    
    # For each gesture, look for multiple images
    for gesture in memes.keys():
        # Look for numbered versions (1,2,3...)
        for i in range(1, 10):  # Check for up to 9 memes per gesture
            filename = f"{gesture}{i}.jpg"
            if os.path.exists(filename):
                img = cv2.imread(filename)
                if img is not None:
                    memes[gesture].append(img)
                    print(f"  ✓ Loaded: {filename}")
        
        # Also look for plain filename
        filename = f"{gesture}.jpg"
        if os.path.exists(filename) and not memes[gesture]:
            img = cv2.imread(filename)
            if img is not None:
                memes[gesture].append(img)
                print(f"  ✓ Loaded: {filename}")
        
        if not memes[gesture]:
            # Create placeholder if no images found
            print(f"  ⚠ No images for {gesture}, creating placeholder")
            placeholder = create_placeholder(gesture)
            memes[gesture].append(placeholder)
    
    return memes

def create_placeholder(gesture):
    """Create colored placeholder meme"""
    names = {
        "thumbs_up": "👍 THUMBS UP! 👍",
        "peace": "✌️ PEACE! ✌️",
        "pointing": "☝️ POINTING! ☝️",
        "open_palm": "🖐️ HIGH FIVE! 🖐️"
    }
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    colors = {
        "thumbs_up": (0, 0, 255),    # Red
        "peace": (0, 255, 0),        # Green
        "pointing": (255, 0, 0),     # Blue
        "open_palm": (0, 255, 255)   # Yellow
    }
    img[:] = colors.get(gesture, (100, 100, 100))
    cv2.putText(img, names.get(gesture, gesture), (50, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    return img

MEMES = load_memes()
total_memes = sum(len(m) for m in MEMES.values())
print(f"\n✓ Loaded {total_memes} memes total")

def recognize_gesture(hand_landmarks):
    """Recognize what gesture you're making"""
    
    # Get fingertip positions
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    
    index_tip = hand_landmarks.landmark[8]
    index_mcp = hand_landmarks.landmark[5]
    
    middle_tip = hand_landmarks.landmark[12]
    middle_mcp = hand_landmarks.landmark[9]
    
    ring_tip = hand_landmarks.landmark[16]
    ring_mcp = hand_landmarks.landmark[13]
    
    pinky_tip = hand_landmarks.landmark[20]
    pinky_mcp = hand_landmarks.landmark[17]
    
    # Check which fingers are up
    index_up = index_tip.y < index_mcp.y
    middle_up = middle_tip.y < middle_mcp.y
    ring_up = ring_tip.y < ring_mcp.y
    pinky_up = pinky_tip.y < pinky_mcp.y
    thumb_up = thumb_tip.y < thumb_ip.y
    
    # Gesture detection
    if thumb_up and not (index_up or middle_up or ring_up or pinky_up):
        return "thumbs_up"
    
    if index_up and middle_up and not ring_up and not pinky_up:
        return "peace"
    
    if index_up and not (middle_up or ring_up or pinky_up):
        return "pointing"
    
    if index_up and middle_up and ring_up and pinky_up:
        return "open_palm"
    
    return None

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("ERROR: Could not open camera!")
    exit()

# Track gestures per hand (for multiple hands)
hand_gestures = {}
hand_hold_counts = {}
hand_meme_showing = {}
hand_current_meme = {}
hand_last_shown_time = {}

print("\n✓ Camera ready!")
print("\n" + "="*50)
print("   GESTURE TO MEME SYSTEM v2.0")
print("="*50)
print("  👍 = Thumbs up")
print("  ✌️ = Peace sign")
print("  ☝️ = Pointing")
print("  🖐️ = Open palm")
print("\n🔥 NEW FEATURES:")
print("  • Multiple hands at once!")
print("  • Random memes each time!")
print("  • Same window for everything!")
print("\n💡 Hold gesture for 1 second to see meme!")
print("Press 'q' to quit\n")

frame_count = 0

while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    # Reset current hand IDs
    current_hand_ids = set()
    
    # Process each detected hand
    if results.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get hand ID (based on position, rough tracking)
            hand_x = hand_landmarks.landmark[0].x
            hand_id = int(hand_x * 10)  # Simple ID based on x position
            
            current_hand_ids.add(hand_id)
            
            # Draw hand landmarks
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
            )
            
            # Recognize gesture
            current_gesture = recognize_gesture(hand_landmarks)
            
            if current_gesture:
                gesture_names = {
                    "thumbs_up": "👍 THUMBS UP! 👍",
                    "peace": "✌️ PEACE SIGN! ✌️",
                    "pointing": "☝️ POINTING! ☝️",
                    "open_palm": "🖐️ OPEN PALM! 🖐️"
                }
                
                # Show gesture name above hand
                wrist = hand_landmarks.landmark[0]
                h, w = frame.shape[:2]
                text_x = int(wrist.x * w) - 50
                text_y = int(wrist.y * h) - 30
                cv2.putText(frame, gesture_names.get(current_gesture, current_gesture), 
                           (max(10, text_x), max(30, text_y)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Track hold count per hand
                if hand_id in hand_gestures and hand_gestures[hand_id] == current_gesture:
                    hand_hold_counts[hand_id] = hand_hold_counts.get(hand_id, 0) + 1
                else:
                    hand_gestures[hand_id] = current_gesture
                    hand_hold_counts[hand_id] = 0
                    hand_meme_showing[hand_id] = False
                
                # Show progress bar for this hand
                if hand_hold_counts.get(hand_id, 0) > 0 and hand_hold_counts[hand_id] < 30:
                    progress = hand_hold_counts[hand_id] / 30
                    bar_x = int(wrist.x * w) - 40
                    bar_y = int(wrist.y * h) - 10
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + 80, bar_y + 5), (100, 100, 100), -1)
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(80 * progress), bar_y + 5), (0, 255, 0), -1)
                
                # Trigger meme when held long enough
                if hand_hold_counts.get(hand_id, 0) > 30 and not hand_meme_showing.get(hand_id, False):
                    # Select a RANDOM meme from the gesture's list
                    if MEMES.get(current_gesture):
                        random_meme = random.choice(MEMES[current_gesture])
                        hand_current_meme[hand_id] = random_meme
                        hand_meme_showing[hand_id] = True
                        hand_last_shown_time[hand_id] = time.time()
            
            else:
                # No gesture - clear this hand's state
                if hand_id in hand_gestures:
                    del hand_gestures[hand_id]
                if hand_id in hand_hold_counts:
                    del hand_hold_counts[hand_id]
                if hand_id in hand_meme_showing:
                    hand_meme_showing[hand_id] = False
    
    # Clean up old hands (that disappeared)
    for hand_id in list(hand_gestures.keys()):
        if hand_id not in current_hand_ids:
            del hand_gestures[hand_id]
            if hand_id in hand_hold_counts:
                del hand_hold_counts[hand_id]
            if hand_id in hand_meme_showing:
                del hand_meme_showing[hand_id]
    
    # DRAW ALL ACTIVE MEMES ON THE SAME WINDOW
    meme_display = frame.copy()
    
    # Position memes around the screen
    meme_positions = [(10, 10), (330, 10), (10, 250), (330, 250)]
    meme_idx = 0
    
    for hand_id, showing in hand_meme_showing.items():
        if showing and hand_id in hand_current_meme:
            meme_img = hand_current_meme[hand_id]
            
            # Resize meme to fit (200x200)
            meme_resized = cv2.resize(meme_img, (300, 300))
            
            # Get position
            x, y = meme_positions[meme_idx % len(meme_positions)]
            
            # Check if we should auto-hide after 3 seconds
            if hand_id in hand_last_shown_time:
                if time.time() - hand_last_shown_time[hand_id] > 3:
                    hand_meme_showing[hand_id] = False
                    continue
            
            # Place meme on the frame
            meme_display[y:y+300, x:x+300] = meme_resized
            
            # Add small indicator of which hand
            cv2.putText(meme_display, f"Hand {hand_id}", (x, y+290), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            meme_idx += 1
    
    # Add instructions on screen
    cv2.putText(meme_display, "Hold gesture to show meme! (Multiple hands supported)", 
               (10, meme_display.shape[0] - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(meme_display, "Press 'q' to quit", 
               (meme_display.shape[1] - 150, meme_display.shape[0] - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # Show active memes count
    active_memes = sum(1 for v in hand_meme_showing.values() if v)
    if active_memes > 0:
        cv2.putText(meme_display, f"Active Memes: {active_memes}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Show everything in ONE window
    cv2.imshow('Gesture to Meme - Multiple Hands & Memes', meme_display)
    
    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✓ Program ended! Thanks for playing!")