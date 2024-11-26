# Project Name

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Deployment](#deployment)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
   - [Running the Application](#running-the-application)
4. [Future Modifications](#future-modifications)
   - [Planned Features](#planned-features)
   - [Potential Improvements](#potential-improvements)
5. [Contributing](#contributing)

## <h2><p id = introduction>Introduction</p></h2>

This is a project for LLM Web Agent

## <h2><p id = features>Features</p></h2>

- Feature 1
- Feature 2
- Feature 3

## <h2><p id = deployment>Deployment</p></h2>

### <h3><p id = prerequisites>Prerequisites</p></h3>

#### Mac/Windows/Linux
#### ollama
#### conda


### <h3><p id = installation>Installation</p></h3>

Provide step-by-step instructions on how to install the project.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/project-name.git
   cd project-name
   ```
2. create conda environment
    ```bash
    conda create --name webagent python=3.9
    conda activate webagent
    ```
3. install necessary package
    ```python
    pip install -r requirements.txt
    ```

## <h2><p id = future-modifications>Future Modifications</p></h2>

### <h3><p id = planned-features>Planned Features</p></h3>

### <h3><p id = potential-improvements>Potential Improvements</p></h3>
###### 1.debugging: handle the error caused by LLM call function and report back to LLM
###### 2.achieve sequential calling (the complex long series tasks)
###### 3.add long term memory for web agent
###### 4.using more advanced prompting techique(LATS ReAct)
###### 5.when program catch the update in web elements, it is need to create the new page sources to follow the update.
###### 6.add opencv to enhance the identification for different elements

