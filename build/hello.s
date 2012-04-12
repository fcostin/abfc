
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
    movq	$0,%rbx
    addb	$0x0a, 0(%rsp, %rbx, 1)
    movb	0(%rsp, %rbx, 1),%al
    testb	%al,%al
    je		end_0000
begin_0000:
    addq        $0x01, %rbx
    addb	$0x07, 0(%rsp, %rbx, 1)
    addq        $0x01, %rbx
    addb	$0x0a, 0(%rsp, %rbx, 1)
    addq        $0x01, %rbx
    addb	$0x03, 0(%rsp, %rbx, 1)
    addq        $0x01, %rbx
    addb	$0x01, 0(%rsp, %rbx, 1)
    subq        $0x04, %rbx
    subb	$0x01, 0(%rsp, %rbx, 1)
    movb	0(%rsp, %rbx, 1),%al
    testb	%al,%al
    jne		begin_0000
end_0000:
    addq        $0x01, %rbx
    addb	$0x02, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq        $0x01, %rbx
    addb	$0x01, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addb	$0x07, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addb	$0x03, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq        $0x01, %rbx
    addb	$0x02, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    subq        $0x02, %rbx
    addb	$0x0f, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq        $0x01, %rbx
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addb	$0x03, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    subb	$0x06, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    subb	$0x08, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq        $0x01, %rbx
    addb	$0x01, 0(%rsp, %rbx, 1)
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq        $0x01, %rbx
    movq	%rbx,%rsi
    addq	%rsp,%rsi
    movq	$1,%rax
    movq	$1,%rdi
    movq	$1,%rdx
    syscall
    addq	$30000,%rsp
    movq	$60,%rax
    movq	$0,%rdi
    syscall
