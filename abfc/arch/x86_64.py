"""
fragments of gnu assembler x86_64 code implementing the various
instructions of the brainfuck machine.
"""

# allocate buff; dp := 0;
#
#   convention : we use %rbx to hold dp, the offset
#                of the data pointer into the buffer
#
#   convention : we make space for the buffer on the stack,
#                with %rsp + %rbx giving the address of
#                the %rbx-th cell in the buffer.
#
#   note :       we must define the global label _start
#                as this is the entry point to our code
#                when we build with gcc using -nostdlib
#
#   note :       we ensure the buffer is initialised to zero
#
#   note :       lastly, we initialise %rbx, the data
#                pointer, to be zero.
PROGRAM_START = r"""
.globl _start
_start:
    start:
    subq	$30000,%rsp
    movq    $0,%rbx
zero_buff_start:
    cmpq    $30000,%rbx
    je      zero_buff_end
    movq    $0x0,0(%rsp,%rbx,1)
    incq    %rbx
    jmp     zero_buff_start
zero_buff_end:
    movq	$0,%rbx"""

# write(stdout, &(buffer[dp]), 1);
#   %rax : which syscall? (0 for write)
#   %rdi : which file descriptor? (1 for stdout)
#   %rsi : which buffer? %rbx + %rsi for dp + buff
#   %rdx : how many bytes to read? (1)
WRITE_CHAR = r"""
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall"""

# read(stdin, &(buffer[dp]), 1);
#   %rax : which syscall? (0 for read)
#   %rdi : which file descriptor? (0 for stdin)
#   %rsi : which buffer? %rbx + %rsi for dp + buff
#   %rdx : how many bytes to read? (1)
READ_CHAR = r"""
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$0,%rax
    movq	$0,%rdi
    movq	$1,%rdx
    syscall"""

DP_RIGHT = r"""
    incq        %rbx"""

DP_LEFT = r"""
    decq	%rbx"""

DP_INC = r"""
    incb	0(%rsp, %rbx, 1)"""

DP_DEC = r"""
    decb	0(%rsp, %rbx, 1)"""

# n.b. we use %al, the low byte of the register %rax as working memory
BEGIN_WHILE_1 = r"""
    movb	0(%rsp, %rbx, 1),%al
    testb	%al,%al
    je		end_"""

BEGIN_WHILE_2 = r"""
begin_"""

BEGIN_WHILE_3 = ":"

# n.b. we use %al, the low byte of the register %rax as working memory
END_WHILE_1 = r"""
    movb	0(%rsp, %rbx, 1),%al
    testb	%al,%al
    jne		begin_"""

END_WHILE_2 = r"""
end_"""

END_WHILE_3 = ":"

# free buff; exit(0)
#   %rax : which syscall? (60 for exit)
#   %rdi : return value
PROGRAM_END = r"""
    addq	$30000,%rsp
    movq	$60,%rax
    movq	$0,%rdi
    syscall
"""

# a few extended versions for run-length encoded output
DP_RIGHT_1 = r"""
    addq        $0x"""
DP_RIGHT_2 = """, %rbx"""

DP_LEFT_1 = r"""
    subq        $0x"""
DP_LEFT_2 = """, %rbx"""

DP_INC_1 = r"""
    addb	$0x"""
DP_INC_2 = """, 0(%rsp, %rbx, 1)"""

DP_DEC_1 = r"""
    subb	$0x"""
DP_DEC_2 = """, 0(%rsp, %rbx, 1)"""

