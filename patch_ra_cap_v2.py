P = "src/Cafe/HW/Espresso/Recompiler/PPCRecompiler.cpp"
c = open(P).read()

# 1) void -> bool + check dimensione all'inizio
old1 = """void PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext_t& ppcImlGenContext)
{
    IMLRegisterAllocatorParameters raParam;"""
new1 = """bool PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext_t& ppcImlGenContext)
{
    size_t totalIML = 0;
    for (auto* seg : ppcImlGenContext.segmentList2)
        totalIML += seg->imlList.size();
    if (totalIML > 8000)
    {
        cemuLog_log(LogType::Force, "[RA SKIP] function too large ({} IML), fallback to interpreter", totalIML);
        return false;
    }

    IMLRegisterAllocatorParameters raParam;"""
assert c.count(old1) == 1, f"old1={c.count(old1)}"
c = c.replace(old1, new1, 1)

# 2) return true; in fondo alla funzione (prima di ApplyIMLPasses, dopo AllocateRegisters)
old2 = "IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);\n}"
new2 = "IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);\n    return true;\n}"
assert c.count(old2) == 1, f"old2={c.count(old2)}"
c = c.replace(old2, new2, 1)

# 3) chiamata: if (!...) return false
old3 = "PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext);"
new3 = "if (!PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext))\n        return false;"
assert c.count(old3) == 1, f"old3={c.count(old3)}"
c = c.replace(old3, new3, 1)

open(P, "w").write(c)
print("[OK] RA cap 8000 applicato")
