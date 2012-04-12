"""
fragments of gnu assembler ia32 code implementing the various
instructions of the brainfuck machine.
"""

PROGRAM_START = r"""
.globl _start
_start:
    start:
    # for(int i = 0; i < 30000; ++i) buff[i] = 0
    subl	$30000,%esp
    movl        $0,%eax
zero_buff_start:
    cmpl        $30000,%eax
    je          zero_buff_end
    movb        $0,0(%esp,%eax,1)
    incl        %eax
    jmp         zero_buff_start
zero_buff_end:
    # initialise data pointer
    movl	$0,%eax"""

WRITE_CHAR = r"""
    movl	%eax,%esi # save eax
    # write(stdout, &(buffer[eax]), 1)
    movl	%eax,%ecx
    addl	%esp,%ecx
    movl	$4,%eax
    movl	$1,%ebx
    movl	$1,%edx
    int		$0x80
    movl	%esi,%eax # restore eax"""

READ_CHAR = r"""
    movl	%eax,%esi # save eax
    # read(stdin, &(buffer[eax]), 1)
    movl	%eax,%ecx
    addl	%esp,%ecx
    movl	$3,%eax
    movl	$0,%ebx
    movl	$1,%edx
    int		$0x80
    movl	%esi,%eax # restore eax"""

DP_RIGHT = r"""
    incl        %eax"""

DP_LEFT = r"""
    decl	%eax"""

DP_INC = r"""
    incb	0(%esp, %eax, 1)"""

DP_DEC = r"""
    decb	0(%esp, %eax, 1)"""

BEGIN_WHILE_1 = r"""
    movb	0(%esp, %eax, 1),%bl
    testb	%bl,%bl
    je		end_"""

BEGIN_WHILE_2 = r"""
begin_"""

BEGIN_WHILE_3 = ":"

END_WHILE_1 = r"""
    movb	0(%esp, %eax, 1),%bl
    testb	%bl,%bl
    jne		begin_"""

END_WHILE_2 = r"""
end_"""

END_WHILE_3 = ":"

PROGRAM_END = r"""
    addl	$30000,%esp
    movl	$1,%eax
    movl	$0,%ebx
    int		$0x80
"""

# a few extended versions for run-length encoded output

DP_RIGHT_1 = r"""
    addl        $0x"""
DP_RIGHT_2 = """, %eax"""

DP_LEFT_1 = r"""
    subl        $0x"""
DP_LEFT_2 = """, %eax"""

DP_INC_1 = r"""
    addb	$0x"""
DP_INC_2 = """, 0(%esp, %eax, 1)"""

DP_DEC_1 = r"""
    subb	$0x"""
DP_DEC_2 = """, 0(%esp, %eax, 1)"""

