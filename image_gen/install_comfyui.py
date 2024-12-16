import os
import subprocess

import requests

# Installation folder
# use two backslashes for windows paths like this D:\\folder\\folder
INSTALL_FOLDER = "D:\\Demos\\Wen\\ComfyUI_windows_portable"


def download_file(url, dest):
    print(f"Downloading {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, "wb") as file:
        file.write(response.content)
    print(f"Downloaded {url} to {dest}")


# Create necessary directories
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")


# Install Manager and Extensions
def install_manager_and_extensions(install_folder):
    custom_nodes_folder = os.path.join(install_folder, "ComfyUI", "custom_nodes")
    if not os.path.exists(custom_nodes_folder):
        print(f"Directory does not exist: {custom_nodes_folder}")
        return
    os.chdir(custom_nodes_folder)
    custom_extensions = [
        "https://github.com/ltdrdata/ComfyUI-Manager",
        "https://github.com/Fannovel16/comfyui_controlnet_aux",
        "https://github.com/BadCafeCode/masquerade-nodes-comfyui",
        "https://github.com/cubiq/ComfyUI_essentials",
        "https://github.com/cubiq/ComfyUI_IPAdapter_plus",
        "https://github.com/rgthree/rgthree-comfy",
        "https://github.com/Lerc/canvas_tab",
        "https://github.com/chrisgoringe/cg-use-everywhere",
        "https://github.com/shadowcz007/comfyui-mixlab-nodes",
        "https://github.com/palant/image-resize-comfyui",
        "https://github.com/GraftingRayman/ComfyUI_GraftingRayman",
        "https://github.com/ai-shizuka/ComfyUI-tbox",
    ]

    for repo_url in custom_extensions:
        repo_name = repo_url.split("/")[-1]
        if os.path.exists(repo_name):
            print(f"Repository {repo_name} already exists. Fetching latest changes...")
            os.chdir(repo_name)
            subprocess.run(["git", "fetch"], check=True)
            subprocess.run(["git", "pull"], check=True)
            os.chdir("..")
        else:
            subprocess.run(["git", "clone", repo_url], check=True)
            print(f"Cloned {repo_url}")


# Download models and put them in the appropriate folders
def download_models(install_folder):
    models_folder = os.path.join(install_folder, "ComfyUI","models")
    if not os.path.exists(models_folder):
        print(f"Directory does not exist: {models_folder}")
        return
    create_directory(os.path.join(models_folder, "checkpoints"))
    create_directory(os.path.join(models_folder, "clip"))
    create_directory(os.path.join(models_folder, "controlnet"))
    create_directory(os.path.join(models_folder, "clip_vision"))
    create_directory(os.path.join(models_folder, "ipadapter"))

    models_dict = {
        # link:path/filename
        "https://huggingface.co/stabilityai/control-lora/resolve/main/control-LoRAs-rank256/control-lora-canny-rank256.safetensors?download=true": os.path.join(
            models_folder, "controlnet", "control-lora-canny-rank256.safetensors"
        ),
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors?download=true": os.path.join(
            models_folder, "ipadapter", "ip-adapter-plus_sdxl_vit-h.safetensors"
        ),
        "https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K/resolve/main/open_clip_pytorch_model.safetensors?download=true": os.path.join(
            models_folder, "clip_vision", "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
        ),
        "https://civitai.com/api/download/models/798204?type=Model&format=SafeTensor&size=full&fp=fp16": os.path.join(
            models_folder,
            "checkpoints",
            "realvisxlV50_v50LightningBakedvae.safetensors",
        ),
    }
    # Download checkpoints
    for link, path in models_dict.items():
        if not os.path.exists(path):
            download_file(link, path)
        else:
            print(f"File already exists: {path}")


# Run installation functions
def main():
    install_folder = INSTALL_FOLDER
    if not os.path.exists(install_folder):
        print(f"Installation folder does not exist: {install_folder}")
        return

    install_manager_and_extensions(install_folder)
    download_models(install_folder)


if __name__ == "__main__":
    main()
