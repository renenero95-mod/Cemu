P = "src/Cafe/HW/Espresso/Recompiler/PPCRecompiler.cpp"
c = open(P).read()

# 1) Cambia signature NativeRegisterAllocatorPass: void -> bool + check dimensione
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
assert c.count(old1) == 1, f"old1 count={c.count(old1)}"
c = c.replace(old1, new1, 1)

# 2) Fine della funzione: aggiungi return true
old2 = """	IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);
}"""
new2 = """	IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);
	return true;
}"""
assert c.count(old2) == 1, f"old2 count={c.count(old2)}"
c = c.replace(old2, new2, 1)

# 3) Chiamante in ApplyIMLPasses: if (!...) return false
old3 = """	PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext);

	return true;
}"""
new3 = """	if (!PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext))
		return false;

	return true;
}"""
assert c.count(old3) == 1, f"old3 count={c.count(old3)}"
c = c.replace(old3, new3, 1)

open(P, "w").write(c)
print("[OK] RA cap a 8000 IML applicato")
