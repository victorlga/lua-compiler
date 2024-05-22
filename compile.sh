#!/bin/bash

# Extract the filename without the extension
filename=$(basename -- "$1")
extension="${filename##*.}"
filename="${filename%.*}"

# Compile the Lua file
python3 main.py "$1"

# Assemble with NASM
nasm -f elf -o "$filename.o" "$filename.asm"

# Link with GCC
gcc -m32 -no-pie -o "$filename" "$filename.o"

# Run the executable
./"$filename"

# Remove temporary files
# rm "$filename.o" "$filename" "$filename.asm"
