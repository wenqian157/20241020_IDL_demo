import os
import subprocess
import requests

def download_file(url, dest):
    print(f"Downloading {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded {url} to {dest}")

# Create necessary directories
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

# Install ComfyUI
def install_comfyui():
    create_directory("ComfyUI")
    comfyui_zip_url = "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z"
    comfyui_zip_path = "ComfyUI/ComfyUI_windows_portable_nvidia.7z"
    download_file(comfyui_zip_url, comfyui_zip_path)

# Install Manager and Extensions
def install_manager_and_extensions():
    os.chdir("ComfyUI/custom_nodes")
    custom_extensions = [
        'https://github.com/ltdrdata/ComfyUI-Manager',
        'https://github.com/cubiq/ComfyUI_essentials',
        'https://github.com/cubiq/ComfyUI_IPAdapter_plus',
        'https://github.com/Fannovel16/comfyui_controlnet_aux',
        'https://github.com/chrisgoringe/cg-use-everywhere',
        'https://github.com/Lerc/canvas_tab'
    ]

    for repo_url in custom_extensions:
        subprocess.run(['git', 'clone', repo_url], check=True)
        print(f"Cloned {repo_url}")

# Download models and put them in the appropriate folders
def download_models():
    create_directory("ComfyUI/models/checkpoints")
    create_directory("ComfyUI/models/clip")
    create_directory("ComfyUI/models/controlnet")
    create_directory("ComfyUI/models/clip_vision")
    create_directory("ComfyUI/models/ipadapter")

    # Download checkpoints
    download_file("https://civitai.com/models/139562/realvisxl-v50", "ComfyUI/models/checkpoints/realvisxl-v50.safetensors")
    download_file("https://huggingface.co/imagepipeline/Copax-TimeLessXL-SDXL1.0/blob/main/copaxTimelessxlSDXL1_v9.safetensors", "ComfyUI/models/checkpoints/copaxTimelessxlSDXL1_v9.safetensors")

    # Download CLIP models
    download_file("https://huggingface.co/lllyasviel/flux1_dev/blob/main/flux1-dev-fp8.safetensors", "ComfyUI/models/clip/flux1-dev-fp8.safetensors")
    download_file("https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors", "ComfyUI/models/clip/clip_l.safetensors")

    # Download ControlNet models
    download_file("https://huggingface.co/stabilityai/control-lora/blob/main/control-LoRAs-rank256/control-lora-canny-rank256.safetensors", "ComfyUI/models/controlnet/control-lora-canny-rank256.safetensors")
    download_file("https://huggingface.co/InstantX/FLUX.1-dev-Controlnet-Canny/blob/main/diffusion_pytorch_model.safetensors", "ComfyUI/models/controlnet/InstantX_FLUX.1-dev-Controlnet-Canny.safetensors")
    download_file("https://huggingface.co/lllyasviel/control_v11p_sd15_normalbae/blob/main/diffusion_pytorch_model.safetensors", "ComfyUI/models/controlnet/control_v11p_sd15_normalbae.safetensors")

    # Download CLIP Vision models
    download_file("https://huggingface.co/h94/IP-Adapter/blob/main/models/image_encoder/model.safetensors", "ComfyUI/models/clip_vision/to-use-with_ip-adapter-plus_sdxl_vit-h.safetensors")

    # Download IP Adapter models
    download_file("https://huggingface.co/h94/IP-Adapter/blob/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors", "ComfyUI/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors")

# Run installation functions
def main():
    install_comfyui()
    install_manager_and_extensions()
    # download_models()

if __name__ == "__main__":
    main()