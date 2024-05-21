from textwrap import dedent

class ASM:

    initial_code = '''
        ; constantes
        SYS_EXIT equ 1
        SYS_READ equ 3
        SYS_WRITE equ 4
        STDIN equ 0
        STDOUT equ 1
        True equ 1
        False equ 0

        segment .data

        formatin: db "%d", 0
        formatout: db "%d", 10, 0 ; newline, nul terminator
        scanint: times 4 db 0 ; 32-bits integer = 4 bytes

        segment .bss  ; variaveis
        res RESB 1

        section .text
        global main ; linux
        ;global _main ; windows
        extern scanf ; linux
        extern printf ; linux
        ;extern _scanf ; windows
        ;extern _printf; windows
        extern fflush ; linux
        ;extern _fflush ; windows
        extern stdout ; linux
        ;extern _stdout ; windows

        ; subrotinas if/while
        binop_je:
        JE binop_true
        JMP binop_false

        binop_jg:
        JG binop_true
        JMP binop_false

        binop_jl:
        JL binop_true
        JMP binop_false

        binop_false:
        MOV EAX, False  
        JMP binop_exit
        binop_true:
        MOV EAX, True
        binop_exit:
        RET

        main:

        PUSH EBP ; guarda o base pointer
        MOV EBP, ESP ; estabelece um novo base pointer

        ; codigo gerado pelo compilador abaixo
    '''

    final_code = '''
        ; interrupcao de saida (default)

        PUSH DWORD [stdout]
        CALL fflush
        ADD ESP, 4

        MOV ESP, EBP
        POP EBP

        MOV EAX, 1
        XOR EBX, EBX
        INT 0x80
    '''

    filename = None

    @staticmethod
    def initialize(filename):
        ASM.filename = filename
        with open(ASM.filename, 'w') as file:
            file.write(dedent(ASM.initial_code))

    @staticmethod
    def write(code):
        if ASM.filename is None:
            raise ValueError("Filename is not set. Call initialize() first.")
        with open(ASM.filename, 'a') as file:
            file.write(dedent(code))

    @staticmethod
    def end():
        if ASM.filename is None:
            raise ValueError("Filename is not set. Call initialize() first.")
        with open(ASM.filename, 'a') as file:
            file.write(dedent(ASM.final_code))