P = "src/Cafe/HW/Espresso/Recompiler/IML/IMLRegisterAllocator.cpp"
c = open(P).read()

if "[REGALLOC DEEP]" in c:
    print("[INFO] Debug già presente, salto.")
else:
    old = """void IMLRegisterAllocator_AllocateRegisters(ppcImlGenContext_t* ppcImlGenContext, IMLRegisterAllocatorParameters& raParam)
{
	IMLRegisterAllocatorContext ctx;"""
    new = """void IMLRegisterAllocator_AllocateRegisters(ppcImlGenContext_t* ppcImlGenContext, IMLRegisterAllocatorParameters& raParam)
{
    auto t0 = std::chrono::steady_clock::now();
	IMLRegisterAllocatorContext ctx;"""
    if old not in c: raise Exception("t0 anchor not found")
    c = c.replace(old, new, 1)

    steps = [
        ("IMLRA_ReshapeForRegisterAllocation(ppcImlGenContext);", "t1"),
        ("IMLRA_CalculateLivenessRanges(ctx);", "t2"),
        ("IMLRA_ProcessFlowAndCalculateLivenessRanges(ctx);", "t3"),
        ("IMLRA_AssignRegisters(ctx, ppcImlGenContext);", "t4")
    ]
    for call, var in steps:
        c = c.replace(call, f"{call}\n    auto {var} = std::chrono::steady_clock::now();", 1)

    old_end = "IMLRA_GenerateMoveInstructions(ctx);"
    new_end = """IMLRA_GenerateMoveInstructions(ctx);
    auto t5 = std::chrono::steady_clock::now();
    auto ms = [](auto a, auto b) { return std::chrono::duration_cast<std::chrono::milliseconds>(b - a).count(); };
    if (ms(t0, t5) > 100) {
        cemuLog_log(LogType::Force, "[REGALLOC DEEP] reshape={}ms liveness={}ms flow={}ms assign={}ms moves={}ms total={}ms",
            ms(t0,t1), ms(t1,t2), ms(t2,t3), ms(t3,t4), ms(t4,t5), ms(t0,t5));
    }"""
    if old_end not in c: raise Exception("t5 anchor not found")
    c = c.replace(old_end, new_end, 1)

    open(P, "w").write(c)
    print("[OK] Aggiunti i timer [REGALLOC DEEP]")
