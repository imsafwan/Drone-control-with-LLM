# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:56:30 2024

@author: mmonda4
"""

import sys


from djitellopy import Tello
import time

from openai import OpenAI
MODEL='gpt-4o'

client = OpenAI(api_key="your key")




# Initialize Tello instance
drone = Tello()
drone.connect()


# Define the skill library to map LLM output to functions
skill_library = {
    "takeoff": lambda: drone.takeoff(),
    "hover": lambda: time.sleep(2),  # Hover for 2 seconds
    "land": lambda: drone.land(),
    "move_f": lambda: drone.move_forward(150),  # Move forward by 150 cm
    "move_b": lambda: drone.move_back(150),  # Move backward by 150 cm
    "full rotation": lambda: drone.rotate_counter_clockwise(360),
    "turn_l": lambda: drone.rotate_counter_clockwise(90),  # Rotate 90 degrees left
    "turn_r": lambda: drone.rotate_clockwise(90),  # Rotate 90 degrees right
    'sleep': lambda: time.sleep(5)
}

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
