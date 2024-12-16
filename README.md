# IDL Demo

by Wenqian Yang and Anton Savov, 2024

# RUN

Complete the [SETUP](#setup) instructions first.
To run this demo you need start its separate components:
1. Sound,
2. Motion Capture,
3. Image Generation and
4. Interaction UI



## 1. SOUND
1. open `filename.ext` in Reaper
2. select sound output `XXX`
3. loop play

## 2. MOCAP
1. Open `Motive`
2. 

## 3. IMAGE GENERATION
1. Start ComfyUI 
2. Drag `image_gen/comfyui_worklfows/workflow_highrise.png` to the ComfyUI canvas. This will open the workflow.
3. set the path in the `LoadImagesFromPath` Node to the `image_gen/screenshot` folder.
4. set the styling image in the `LoadImage` node below the `LoadImagesFromPath` node to the `image_gen/workflows/styling_reference_01.png`
5. ...

## 4. INTERACTION UI
1. Open a new Command Prompt and activate the environment:
    
        conda activate idldemo
2. cd to `image_gen` folder
3. run `python IDL_3D_mocap.py`


# SETUP

This demo is made for WS3 (Alba) in the IDL.

## 1. Conda environment

    conda create -n idldemo python=3.13.0
    conda activate idldemo
    pip install -r requirements.txt

## 2. ComfyUI

1. Install the `portable standalone build` for Windows of [ComfyUI](https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file#installing). You need 7-zip to unzip it.
2. Set the `INSTALL_FOLDER` variable in `image_gen\install_compfy.py` to the folder in which your `ComfyUI` folder is located.
3. Run `python install_compfy.py` to download and install extensions and models. This will take some time.
4. Test by running




## DONT DO, BUT On windows (ONLY IF YOU NEED GLUT)

from: https://stackoverflow.com/questions/65699670/pyopengl-opengl-error-nullfunctionerror-attempt-to-call-an-undefined-functio


clone the repository:

git clone https://github.com/mcfletch/pyopengl
install pyopengl and pyopengl_accelerate:

cd pyopengl
pip install -e .
cd accelerate
pip install -e .