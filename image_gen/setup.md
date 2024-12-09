
# run ai image generation

1. start ComfyUI (setup instructions are below)
2. drag the workflow_highrise.png image from folder _gitrepo_/image_gen/workflows onto the comfyUI canvas. this will open the workflow
3. in the LoadImagesFromPath Node set the path to _gitrepo_/image_gen/screenshot
4. set the styling image in the LoadImage node below the LoadImagesFromPath node to the styling_reference.png image from _gitrepo_/image_gen/workflows

# install ComfyUI

## On Windows and with nvidia card

1. install [ComfyUI](https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file#installing)
2. [direct download for the portable distribution link here](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z)


3. update the install folder in `install_compfy.py`. set it to the folder in which your `ComfyUI` folder is located.
4. run `python install_compfy.py` to download and install extensions and models.

5. start comfyUI with `run_nvidia_gpu.bat` from the portable distribution folder. It will install some stuff and stop at "press any key to continue" several times. each time start it over from the bat file again until the comfyUI server starts.
6. once the comfyUI opens in the browser, click on the cogwheel for settings and in comfyui settings select BETA Menu Enable Top.
7. Then click on Manager and in "Custom Nodes Manager" Filter to "installed". For all that failed click Try Fix. Then click restart. Confirm with OK to reboot the server. Once it reboots, check again if all installed nodes loaded properly. if not repeat this step.


# Older notes for refernce

5. install manager [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)

run ComfyUI and in the manager install the following:
1. install [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials)
2. install with manager [ComfyUI_IPAdapter_plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
3. install [ComfyUI's ControlNet Auxiliary Preprocessors](https://github.com/Fannovel16/comfyui_controlnet_aux)
4. install [Use Everywhere (UE Nodes)](https://github.com/chrisgoringe/cg-use-everywhere)
5. install [Canvas Tab](https://github.com/Lerc/canvas_tab)

## models

https://civitai.com/models/139562/realvisxl-v50

Use Turbo models with DPM++ SDE Karras sampler, 4-10 steps and CFG Scale 1-2.5
Use Lightning models with DPM++ SDE Karras / DPM++ SDE sampler, 4-6 steps and CFG Scale 1-2

put in ComfyUI/models/checkpoints
https://huggingface.co/imagepipeline/Copax-TimeLessXL-SDXL1.0/blob/main/copaxTimelessxlSDXL1_v9.safetensors

put in ComfyUI/models/clip/
https://huggingface.co/lllyasviel/flux1_dev/blob/main/flux1-dev-fp8.safetensors
https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors

put in ComfyUI/models/controlnet
https://huggingface.co/stabilityai/control-lora/blob/main/control-LoRAs-rank256/control-lora-canny-rank256.safetensors

https://huggingface.co/InstantX/FLUX.1-dev-Controlnet-Canny/blob/main/diffusion_pytorch_model.safetensors
and rename to InstantX_FLUX.1-dev-Controlnet-Canny.safetensors

https://huggingface.co/lllyasviel/control_v11p_sd15_normalbae/blob/main/diffusion_pytorch_model.safetensors
and rename to control_v11p_sd15_normalbae.safetensors

put in ComfyUI/models/clip_vision
https://huggingface.co/h94/IP-Adapter/blob/main/models/image_encoder/model.safetensors
and rename to to-use-with_ip-adapter-plus_sdxl_vit-h.safetensors


put in ComfyUI/models/ipadapter
https://huggingface.co/h94/IP-Adapter/blob/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors

# refs

https://docs.runware.ai/en/image-inference/models 

https://docs.runware.ai/en/getting-started/introduction 

https://civitai.com/models/8552/dvarch-multi-prompt-architecture-tuned-model

## tutorials

https://stable-diffusion-art.com/ip-adapter/


The Ultimate ControlNet Tutorial: Understanding UNet, Exploring Pro Max, & Kolor's New Model, by Amir Ferdos, https://www.youtube.com/watch?v=1xk8Y5FiD8A


https://github.com/pydn/ComfyUI-to-Python-Extension 

https://www.runcomfy.com/tutorials/mastering-controlnet-in-comfyui

https://openart.ai/workflows/cgtips/comfyui-basic---convert-sketch-to-digital-image/rSmBJheN9S4ToS3Zfc6N 

ComfyUI Scribbles to Masterpieces Workflow! - https://www.youtube.com/watch?v=YhoPsuHA_LA


# Stable diffusion

## resolutions for SDXL
stable-diffusion-xl-1024-v0-9 supports generating images at the following dimensions:

- 1024 x 1024 = 1 : 1
- 1152 x 896 = 1,2857142857 : 1
- 896 x 1152 
- 1216 x 832 = 1,4615384615 : 1
- 832 x 1216
- 1344 x 768 = 1,75 : 1
- 768 x 1344
- 1536 x 640 = 2,4 : 1
- 640 x 1536