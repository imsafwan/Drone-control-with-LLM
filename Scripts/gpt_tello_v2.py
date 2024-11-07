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
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import matplotlib.pyplot as plt

MODEL='gpt-4o'
client = OpenAI(api_key="your API key")


import time
from djitellopy import Tello
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import cv2
import torch

# Initialize the Tello drone
drone = Tello()
drone.connect()
drone.streamon()
image_counter = 0

# Initialize BLIP model and processor for captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Define a skill library for drone actions
skill_library = {
    "takeoff": lambda: drone.takeoff(),
    "hover": lambda: time.sleep(2),
    "land": lambda: drone.land(),
    "move_f": lambda: drone.move_forward(150),
    "move_b": lambda: drone.move_back(150),
    "full_rotation": lambda: drone.rotate_counter_clockwise(360),
    "turn_l": lambda: drone.rotate_counter_clockwise(90),
    "turn_r": lambda: drone.rotate_clockwise(90),
    "sleep": lambda: time.sleep(1),
    "take_picture": lambda: capture_image(),
    "scan": lambda target_object=None: perform_scan(target_object)
}

def is_similar_with_llm(target_object, caption):
    # Construct an optimized prompt for the LLM
    prompt = (
        f"In the description '{caption}', is there an object similar to or related to '{target_object}'? "
        "Respond with 'yes' or 'no' only. "
        "Example: If description is 'A bottle on a table' and target is 'water jar', respond 'yes'."
    )
    print(prompt)
    
    # Call the LLM using GPT-4-turbo or GPT-3.5-turbo
    response = client.chat.completions.create(
        model="gpt-4o",  # Replace with "gpt-3.5-turbo" if preferred
        messages=[
            {"role": "system", "content": "You are an assistant that determines if a target object is found in a scene."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5,
        temperature=0  # Keep temperature low for deterministic responses
    )
    
    # Extract the response
    answer = response.choices[0].message.content.strip()
    
    
    # Determine if the LLM considers them similar
    return answer.lower().startswith("yes")



# Capture an image and save it locally
def capture_image():
    global image_counter
    frame = drone.get_frame_read().frame
    if frame is not None:
        filename = f"image_{image_counter}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Captured and saved image: {filename}")
        image_counter += 1
        return filename
    else:
        print("Failed to capture image.")
        return None

# Generate a caption for the image using BLIP
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        caption_ids = model.generate(**inputs)
        caption = processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption

# Perform a 360-degree scan and use BLIP to find the target object
def perform_scan(target_object=None, interval=45):
    global image_counter
    image_counter = 0
    spatial_descriptions = []
    found_target = False

    # Capture images at intervals around a 360-degree rotation
    for angle in range(0, 360, interval):
        image_path = capture_image()
        if image_path:
            # Generate a caption for the captured image
            caption = generate_caption(image_path)
            spatial_descriptions.append(f"At {angle} degrees: {caption}")
            
            
            
            # Check if the target object is mentioned in the caption
            print('caption---->', caption)
            res = is_similar_with_llm(target_object, caption)
            
             
            if target_object and res:
                print(f"Found an object similar to '{target_object}' at {angle} degrees: {caption}")
                found_target = True
                
                # Take a picture of the identified object
                filename = capture_image()
                if filename:
                    # Plot the image using matplotlib
                    img = Image.open(filename)
                    plt.imshow(img)
                    plt.axis("off")
                    plt.title(f"Detected '{target_object}' at {angle} degrees")
                    plt.show()
        if found_target:
            break
                

        # Rotate the drone to the next angle
        drone.rotate_clockwise(interval)
        time.sleep(1)

    # Print all spatial descriptions
    print("Spatial Descriptions of Surroundings:")
    for description in spatial_descriptions:
        print(description)

    return found_target

# Get user input for the natural language command
command = input("Enter the command for the drone: ")

# Construct the prompt for the LLM
prompt = f"""
You are a robot capable of performing actions from a limited set of skills: {', '.join(skill_library.keys())}.
Identify any target object in the command if specified, and translate the following natural language command into a sequence of actions, using only these skills. If no target object is specified, simply include "scan" in the action sequence.

Example:
Command: please takeoff and try to find an apple to take a picture of it and land
Output: Target Object: apple | Action Sequence: takeoff -> sleep -> scan -> sleep -> land

Command: "{command}"
Output:
"""  

# Generate the action sequence and target object using the LLM
completion = client.chat.completions.create(
    model= MODEL,  
    messages=[{"role": "user", "content": prompt}]
)

response = completion.choices[0].message.content.strip()
print("LLM Response:", response)

# Parse the response to extract the target object and action sequence
target_object = ""
action_sequence = ""

if "Target Object:" in response and "Action Sequence:" in response:
    # Split response into parts for target object and action sequence
    parts = response.split("|")
    for part in parts:
        if "Target Object:" in part:
            target_object = part.split("Target Object:")[1].strip()
        elif "Action Sequence:" in part:
            action_sequence = part.split("Action Sequence:")[1].strip()

# If no target object is specified, handle it as a general scan
if not target_object:
    print("No target object specified. Performing a general scan.")
    target_object = None  # Proceed with a general scan if no specific target

# Translate LLM output action sequence into a list of commands
actions = action_sequence.split(" -> ")

confirm = input("Execute action? (y/n): ").strip().lower()

if confirm == 'y':
    # Execute the action sequence with conditional checks
    for action in actions:
        action = action.strip().lower()

        # Execute each action in the skill library
        if action in skill_library:
            if action == "scan":
                found_target = skill_library["scan"](target_object)
                if found_target and target_object:
                    print('<-------Finished-------->')
            else:
                skill_library[action]()  # Execute other actions
        else:
            print(f"Warning: No executable skill found for '{action}'")  
else:
    print("Skipped action execution.")

# End session
drone.end()