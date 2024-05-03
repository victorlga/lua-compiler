python3 main.py test.lua
nasm -f elf -o test.o test.asm
gcc -m32 -no-pie -o test test.o
./test