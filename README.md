# IDL Demo

by Wenqian Yang and Anton Savov, 2024

This demo is developed for the [Immersive Design Lab (IDL)](https://idl.ethz.ch/website/) at [Design++, ETH Zurich](https://designplusplus.ethz.ch).

# RUN

Complete the [SETUP](#setup) instructions first.
To run this demo you need to start its separate components:
1. Sound,
2. Motion Capture,
3. Image Generation and
4. Interaction UI



## 1. SOUND
1. open `sounds/demo_reaper.rpp` in Reaper
2. select sound output `DAW Out Multiout channel`
3. open holophonix server in the browser 10.255.255.60
4. loop play

## 2. MOCAP
1. Open `Motive`
2. Set to Loopback in the streaming pane.
3. In the Assets Pane make sure GTR and VOC are checked. Those are the tracked markers

## 3. IMAGE GENERATION
1. Start ComfyUI from the run_nvdia_gpu.bat file
2. Drag `image_gen/comfyui_worklfows/workflow_highrise.png` to the ComfyUI canvas. This will open the workflow.
3. set the path in the `LoadImagesFromPath` Node to the `image_gen/screenshot` folder.
4. set the styling image in the `LoadImage` node below the `LoadImagesFromPath` node to the `image_gen/workflows/styling_reference_01.png`
5. Switch to "Queue on change", press play and leave it open.

## 4. INTERACTION UI
1. Open a new Anaconda Command Prompt and activate the environment:
    
        conda activate idldemo
2. cd to `code` folder in the demo git repo
3. run `python IDL_mocap_to_image_holophonix.py`

## 5. PLAY
1. Pretend your are holding a bow and pointing an arrow. GTR tracker is the tip of the arrow, VOC is the back.
2. You control the postion of the blue box with where the tip is pointed at and its size by how much you "pull the bow", i.e. distance between markers.
3. Once you like a location press the mouse button to generate the image. Press again to enable interaction again.


# SETUP

This demo is made for WS3 (Alba) in the IDL.

## 1. Conda environment

    conda create -n idldemo python=3.13.0
    conda activate idldemo
    pip install -r requirements.txt

## 2. ComfyUI

1. Install ComfyUI: install the `portable standalone build` for Windows of [ComfyUI](https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file#installing). You need 7-zip to unzip it.
2. Set the `INSTALL_FOLDER` variable in `image_gen\install_compfy.py` to the folder in which your `ComfyUI` folder is located.
3. Run `python install_compfy.py` to download and install extensions and models. This will take some time.
4. Start ComfyUI by "ComfyUI_windows_portable\run_nvidia_gpu.bat". This will begin initializing the various modules and dependencies and might reach a state "press any key to continue" after which it will simply exit. Then run again as many times as needed until the ComfyUI Canvas opens in the default browser.
5. In the ComfyUI click on "Manager". Then click on "Custom Nodes Manager". In Filter choose "Installed". Then click on all that have  "Try to update" especially the ones that light up with some errors and have a "Try Fix" button. Restart ComfyUI.
4. Drag `image_gen/comfyui_worklfows/workflow_highrise.png` to the ComfyUI canvas. This will open the workflow.
5. set the path in the `LoadImagesFromPath by Mixlabs` Node to the `image_gen/screenshot` folder.
6. set the styling image in the `LoadImage` node below the `LoadImagesFromPath` node to the `image_gen/workflows/styling_reference_01.png`
7. Test by running