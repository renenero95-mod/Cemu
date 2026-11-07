P = "src/Cafe/HW/Espresso/Recompiler/IML/IMLRegisterAllocator.cpp"
c = open(P).read()
if "[MERGE SLOW]" in c:
    print("[INFO] timer già presente")
else:
    old = "void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)\n{\n\tfor (size_t s = 0"
    new = "void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)\n{\n\tauto startT = std::chrono::steady_clock::now();\n\tfor (size_t s = 0"
    if old not in c: raise Exception("anchor1")
    c = c.replace(old, new, 1)
    
    # Aggiungi timer alla fine: trova la graffa di chiusura della funzione
    start = c.find("void IMLRA_MergeCloseAbstractRanges")
    depth = 0
    started = False
    end = -1
    for i in range(start, len(c)):
        if c[i] == '{':
            depth += 1
            started = True
        elif c[i] == '}':
            depth -= 1
            if started and depth == 0:
                end = i
                break
    if end == -1: raise Exception("no end")
    
    timer = "\n\tauto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - startT).count();\n\tif (ms > 100)\n\t\tcemuLog_log(LogType::Force, \"[MERGE SLOW] {}ms ({} segments)\", ms, ctx.deprGenContext->segmentList2.size());\n"
    c = c[:end] + timer + c[end:]
    open(P, "w").write(c)
    print("[OK] timer [MERGE SLOW] aggiunto")
