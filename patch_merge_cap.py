P = "src/Cafe/HW/Espresso/Recompiler/IML/IMLRegisterAllocator.cpp"
c = open(P).read()

old = """void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)
{
	auto startT = std::chrono::steady_clock::now();
	for (size_t s = 0; s < ctx.deprGenContext->segmentList2.size(); s++)
	{
		IMLSegment* imlSegment = ctx.deprGenContext->segmentList2[s];
		if (!imlSegment->list_prevSegments.empty())
			continue; // not an entry/standalone segment
		PPCRecRA_followFlowAndExtendRanges(ctx, imlSegment);
	}
	auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - startT).count();
	if (ms > 100)
		cemuLog_log(LogType::Force, "[MERGE SLOW] {}ms ({} segments)", ms, ctx.deprGenContext->segmentList2.size());
}"""

new = """void IMLRA_MergeCloseAbstractRanges(IMLRegisterAllocatorContext& ctx)
{
	size_t segmentCount = ctx.deprGenContext->segmentList2.size();
	if (segmentCount > 1200)
	{
		cemuLog_log(LogType::Force, "[MERGE CAP] skipping MergeClose ({} segments)", segmentCount);
		return;
	}
	auto startT = std::chrono::steady_clock::now();
	for (size_t s = 0; s < segmentCount; s++)
	{
		IMLSegment* imlSegment = ctx.deprGenContext->segmentList2[s];
		if (!imlSegment->list_prevSegments.empty())
			continue;
		PPCRecRA_followFlowAndExtendRanges(ctx, imlSegment);
	}
	auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - startT).count();
	if (ms > 100)
		cemuLog_log(LogType::Force, "[MERGE SLOW] {}ms ({} segments)", ms, segmentCount);
}"""

if old not in c: raise Exception(f"anchor count={c.count(old)}")
open(P, "w").write(c.replace(old, new, 1))
print("[OK] cap MergeClose a 1200 segmenti")
