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
3 **OpenAI API Client Library**  
   Install OpenAI's API client library:
   ```bash
   pip install openai
   ```


## Running the Script

### Clone the Repository
1. To start, clone this repository into your local environment:
```bash
git clone https://github.com/yourusername/drone_control_with_llm.git
```


2. To execute the main script:

```bash
Copy code
python gpt_tello.py
```

  