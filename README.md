Editar Makefile

gpu=1

ccap=75 De acordo com sua GPU Nvidia

CXX        = g++-9

CUDA       = /usr/local/cuda-12.8 De acordo com sua instalação

CXXCUDA    = /usr/bin/g++-9

NVCC       = nvcc

--------------------------------------------------------------------------------------------------------------------------------------

sudo apt install python3-venv

python3 -m venv myenv

source myenv/bin/activate

sudo apt install g++-9 -y

sudo apt install build-essential -y

sudo apt install libssl-dev -y

sudo apt install libgmp-dev -y

pip install python-telegram-bot

make clean

make all

./vanitysearch -t 0 -gpu -gpuId 0 -g 1792 -o Found.txt --keyspace 80000000000000000:fffffffffffffffff 1MVDYgVa
