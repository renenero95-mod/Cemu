P = "src/Cafe/HW/Espresso/Recompiler/PPCRecompiler.cpp"
c = open(P).read()

# Trova la funzione
old = """bool PPCRecompiler_ApplyIMLPasses(ppcImlGenContext_t& ppcImlGenContext)
{
	// isolate entry points from function flow (enterable segments must not be the target of any other segment)
	// this simplifies logic during register allocation
	PPCRecompilerIML_isolateEnterableSegments(&ppcImlGenContext);

	// merge certain float load+store patterns
	IMLOptimizer_OptimizeDirectFloatCopies(&ppcImlGenContext);
	// delay byte swapping for certain load+store patterns
	IMLOptimizer_OptimizeDirectIntegerCopies(&ppcImlGenContext);

	IMLOptimizer_StandardOptimizationPass(ppcImlGenContext);

	PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext);

	return true;
}"""

new = """bool PPCRecompiler_ApplyIMLPasses(ppcImlGenContext_t& ppcImlGenContext)
{
    auto t0 = std::chrono::steady_clock::now();
    
	PPCRecompilerIML_isolateEnterableSegments(&ppcImlGenContext);
    auto t1 = std::chrono::steady_clock::now();

	IMLOptimizer_OptimizeDirectFloatCopies(&ppcImlGenContext);
	IMLOptimizer_OptimizeDirectIntegerCopies(&ppcImlGenContext);
    auto t2 = std::chrono::steady_clock::now();

	IMLOptimizer_StandardOptimizationPass(ppcImlGenContext);
    auto t3 = std::chrono::steady_clock::now();

	PPCRecompiler_NativeRegisterAllocatorPass(ppcImlGenContext);
    auto t4 = std::chrono::steady_clock::now();

    auto ms = [](auto a, auto b) { return std::chrono::duration_cast<std::chrono::milliseconds>(b - a).count(); };
    uint64_t total = ms(t0, t4);
    
    if (total > 100) {
        cemuLog_log(LogType::Force, "[OPT SLOW] isolate={}ms float/int={}ms std={}ms regalloc={}ms total={}ms",
            ms(t0,t1), ms(t1,t2), ms(t2,t3), ms(t3,t4), total);
    }

	return true;
}"""

assert c.count(old) == 1, "Pattern non trovato"
c = c.replace(old, new, 1)
open(P, "w").write(c)
print("[OK] Aggiunti log [OPT SLOW] per i sotto-passaggi")
