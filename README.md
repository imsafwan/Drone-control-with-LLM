# Drone Control with Natural Language Commands

## Overview
This project demonstrates a natural language-driven control of a Tello drone using a Large Language Model (LLM). The system interprets natural language commands, converts them into drone actions, and executes them in sequence. The commands are processed using OpenAI's LLM (e.g., GPT-4) to generate specific drone actions like takeoff, landing, hovering, and directional movements.


## Dependencies

### Required Libraries
1. **Python 3.10** or above
2. **`djitellopy`** - A library to interface with the DJI Tello drone.
   ```bash
   pip install djitellopy
   ```
3. **OpenAI API Client Library**  
   Install OpenAI's API client library:
   ```bash
   pip install openai
   ```
4. ** Transfomer Library ** 
Install the `transformers` library for Vision-Language Model (VLM) support, e.g., BLIP:
```bash
pip install transformers
```

## Running the Scripts

### Clone the Repository
1. To start, clone this repository into your local environment:
```bash
git clone https://github.com/imsafwan/Drone-control-with-LLM.git
```

## Demo Scripts

## Demo Scripts

### 1. Demo 1: Basic Drone Control with Textual Instructions
In Demo 1, the LLM interprets textual instructions by breaking them down into smaller, executable actions based on the drone’s skill set. These actions are then mapped to lower-level control functions using the `djitellopy` API.

To run Demo 1:
```bash
cd Scripts
python gpt_tello.py
```
Demo 1
[![YouTube](http://i.ytimg.com/vi/5HCtiNPGZvM/hqdefault.jpg)](https://www.youtube.com/watch?v=5HCtiNPGZvM)


### 2. Demo 2: Drone Control with Object Identification
Demo 2 expands on Demo 1 by adding object detection capabilities. After receiving instructions, the LLM directs the drone to scan its surroundings and take images. These images are then sent to a Vision-Language Model (VLM) to generate captions. The LLM checks if the target object appears in the captions, and if so, the drone captures a photo of it.

To run Demo 2:
1. Ensure transformers (for the BLIP model) is installed.

2. Run main script
```bash
cd Scripts
python gpt_tello_v2.py
```
Demo 2
[![YouTube](http://i.ytimg.com/vi/5HCtiNPGZvM/hqdefault.jpg)](https://www.youtube.com/watch?v=5HCtiNPGZvM)

  
  