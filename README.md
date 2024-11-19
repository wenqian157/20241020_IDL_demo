# SETUP

    conda create -n idldemo python=3.13.0
    conda activate idldemo
    pip install -r requirements.txt

## DONT DO, BUT On windows (ONLY IF YOU NEED GLUT)

from: https://stackoverflow.com/questions/65699670/pyopengl-opengl-error-nullfunctionerror-attempt-to-call-an-undefined-functio


clone the repository:

git clone https://github.com/mcfletch/pyopengl
install pyopengl and pyopengl_accelerate:

cd pyopengl
pip install -e .
cd accelerate
pip install -e .