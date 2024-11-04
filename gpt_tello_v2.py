# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 15:10:40 2024

@author: mmonda4
"""


import sys
import cv2
import numpy as np
from djitellopy import Tello
import time
from openai import OpenAI

MODEL='gpt-4o'

client = OpenAI(api_key="your key")




# Initialize Tello instance
drone = Tello()
drone.connect()
image_counter = 0


skill_library = {
    "takeoff": lambda: drone.takeoff(),
    "hover": lambda: time.sleep(2),  # Hover for 2 seconds
    "land": lambda: drone.land(),
    "move_f": lambda: drone.move_forward(150),  # Move forward by 150 cm
    "move_b": lambda: drone.move_back(150),  # Move backward by 150 cm
    "full_rotation": lambda: drone.rotate_counter_clockwise(360),
    "turn_l": lambda: drone.rotate_counter_clockwise(90),  # Rotate 90 degrees left
    "turn_r": lambda: drone.rotate_clockwise(90),  # Rotate 90 degrees right
    "sleep": lambda: time.sleep(5),
    
    # New skill: Take a picture
    "take_picture": lambda: capture_image(),
    
    # New skill: Perform a 360-degree scan and capture images
    "scan": lambda: perform_scan()
}

# Function to capture an image and save it locally
def capture_image():
    global image_counter
    # Start the video stream if not already on
    if not drone.streamon:
        drone.streamon()
    frame = drone.get_frame_read().frame
    if frame is not None:
        filename = f"image_{image_counter}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Captured and saved image: {filename}")
        image_counter += 1
    else:
        print("Failed to capture image.")

# Function to perform a 360-degree scan by taking pictures at regular intervals
def perform_scan(interval=45):
    """
    Rotates the drone by `interval` degrees and captures images at each position.
    Completes a full 360-degree rotation.
    """
    global image_counter
    image_counter = 0  # Reset image counter for a new scan

    # Capture images in 360 degrees
    for _ in range(360 // interval):
        capture_image()                   # Capture an image at the current position
        drone.rotate_clockwise(interval)  # Rotate the drone by the specified interval
        time.sleep(2)                     # Allow some time to stabilize after rotation
    print("Completed 360-degree scan.")
    
    # Stitch the captured images into a panoramic view
    pano = stitch_images()
    return pano

# Function to stitch images into a panoramic view
def stitch_images():
    images = []
    # Load captured images
    for i in range(image_counter):
        filename = f"image_{i}.jpg"
        img = cv2.imread(filename)
        if img is not None:
            images.append(img)

    # Use OpenCV’s stitcher to create a panoramic view
    stitcher = cv2.Stitcher.create()
    status, pano = stitcher.stitch(images)
    
    if status == cv2.Stitcher_OK:
        cv2.imwrite("panorama.jpg", pano)
        print("Panorama created and saved as 'panorama.jpg'")
        return pano
    else:
        print("Failed to create panorama. Stitching error.")
        return None  # Return None if stitching fails





# Get user input for the natural language command
command = input("Enter the command for the drone: ")

# Construct the prompt for the LLM
prompt = f"""
You are a robot capable of performing actions from a limited set of skills: {', '.join(skill_library.keys())}.
Translate the following natural language command into a sequence of actions, using only these skills.

Example:
Command: please takeoff and then hover and land
Output: takeoff -> sleep-> hover -> sleep -> land

Command: "{command}"
Output:
"""  

# Generate the action sequence using LLM
completion = client.chat.completions.create(
  model=MODEL,
  messages=[{"role": "user", "content": prompt}]
)
action_sequence = completion.choices[0].message.content.strip()
print("Action Sequence from LLM:", action_sequence)

# Translate LLM output into a list of commands
actions = action_sequence.split(" -> ")


confirm = input("Execute action ? (y/n): ").strip().lower()

if confirm == 'y':
    # Execute the action sequence with confirmation
    for action in actions:
        skill = skill_library.get(action.strip().lower())  # Strip whitespace and ensure case-insensitivity
        if skill:
            skill()  # Execute the skill function if confirmed
           
        else:
            print(f"Warning: No executable skill found for '{action}'")  
else:
     print(f"Skipped action git init")

# End session
drone.end()