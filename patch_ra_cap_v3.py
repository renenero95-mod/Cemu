P = "src/Cafe/HW/Espresso/Recompiler/PPCRecompiler.cpp"
c = open(P).read()

# 1) void -> bool + check dimensione (usa TAB)
old1 = "void PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext_t& ppcImlGenContext)\n{\n\tIMLRegisterAllocatorParameters raParam;"
new1 = "bool PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext_t& ppcImlGenContext)\n{\n\tsize_t totalIML = 0;\n\tfor (auto* seg : ppcImlGenContext.segmentList2)\n\t\ttotalIML += seg->imlList.size();\n\tif (totalIML > 8000)\n\t{\n\t\tcemuLog_log(LogType::Force, \"[RA SKIP] function too large ({} IML), fallback to interpreter\", totalIML);\n\t\treturn false;\n\t}\n\n\tIMLRegisterAllocatorParameters raParam;"
assert c.count(old1) == 1, f"old1={c.count(old1)}"
c = c.replace(old1, new1, 1)

# 2) return true alla fine (dopo AllocateRegisters)
old2 = "IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);\n}"
new2 = "IMLRegisterAllocator_AllocateRegisters(&ppcImlGenContext, raParam);\n\treturn true;\n}"
assert c.count(old2) == 1, f"old2={c.count(old2)}"
c = c.replace(old2, new2, 1)

# 3) chiamata con if
old3 = "\tPPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext);"
new3 = "\tif (!PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext))\n\t\treturn false;"
assert c.count(old3) == 1, f"old3={c.count(old3)}"
c = c.replace(old3, new3, 1)

open(P, "w").write(c)
print("[OK] RA cap 8000 applicato")
