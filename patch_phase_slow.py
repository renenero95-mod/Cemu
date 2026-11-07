P = "src/Cafe/HW/Espresso/Recompiler/PPCRecompiler.cpp"
c = open(P).read()

# Inserisci timer per generateIML
old1 = "bool compiledSuccessfully = PPCRecompiler_generateIntermediateCode(ppcImlGenContext, ppcRecFunc, entryAddresses, boundaryTracker);"
new1 = """auto phaseStart = std::chrono::steady_clock::now();
    bool compiledSuccessfully = PPCRecompiler_generateIntermediateCode(ppcImlGenContext, ppcRecFunc, entryAddresses, boundaryTracker);
    uint64_t imlMs = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - phaseStart).count();"""

# Inserisci timer per ApplyIMLPasses
old2 = "if (!PPCRecompiler_ApplyIMLPasses(ppcImlGenContext))"
new2 = """phaseStart = std::chrono::steady_clock::now();
    bool passesOk = PPCRecompiler_ApplyIMLPasses(ppcImlGenContext);
    uint64_t passMs = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - phaseStart).count();
    if (!passesOk)"""

# Inserisci timer per AArch64
old3 = "bool aarch64GenerationSuccess = PPCRecompiler_generateAArch64Code(ppcRecFunc, &ppcImlGenContext);"
new3 = """phaseStart = std::chrono::steady_clock::now();
    bool aarch64GenerationSuccess = PPCRecompiler_generateAArch64Code(ppcRecFunc, &ppcImlGenContext);
    uint64_t a64Ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - phaseStart).count();
    
    if (imlMs + passMs + a64Ms > 100)
        cemuLog_log(LogType::Force, "[PHASE SLOW] pc=0x{:08X} IML={}ms Opt={}ms A64={}ms", range.startAddress, imlMs, passMs, a64Ms);
"""

assert c.count(old1) == 1
assert c.count(old2) == 1
assert c.count(old3) == 1

c = c.replace(old1, new1, 1)
c = c.replace(old2, new2, 1)
c = c.replace(old3, new3, 1)

open(P, "w").write(c)
print("[OK] Aggiunti log [PHASE SLOW]")
