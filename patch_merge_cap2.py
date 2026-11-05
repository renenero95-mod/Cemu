P = "src/Cafe/HW/Espresso/Recompiler/IML/IMLRegisterAllocator.cpp"
c = open(P).read()

old = "void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)\n{\n\tauto startT = std::chrono::steady_clock::now();\n\tfor (size_t s = 0; s < ctx.deprGenContext->segmentList2.size(); s++)"
new = "void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)\n{\n\tsize_t segmentCount = ctx.deprGenContext->segmentList2.size();\n\tif (segmentCount > 1200) { cemuLog_log(LogType::Force, \"[MERGE CAP] skip ({} segments)\", segmentCount); return; }\n\tauto startT = std::chrono::steady_clock::now();\n\tfor (size_t s = 0; s < segmentCount; s++)"

assert c.count(old) == 1, f"count={c.count(old)}"
open(P, "w").write(c.replace(old, new, 1))
print("[OK] cap MergeClose a 1200")
