P = "src/util/CemuDiagV2.h"
c = open(P).read()
old = "const uint64_t ns = static_cast<uint64_t>(elapsedNs);\n            g_jitCount.fetch_add(1"
new = """const uint64_t ns = static_cast<uint64_t>(elapsedNs);
            if (ns > 100000000ULL)
                cemuLog_log(LogType::Force, "[JIT SLOW] pc=0x{:08X} ms={}", m_ppcAddress, ns / 1000000ULL);
            g_jitCount.fetch_add(1"""
assert c.count(old) == 1, f"old trovato {c.count(old)} volte"
open(P, "w").write(c.replace(old, new, 1))
print("[OK] [JIT SLOW] aggiunto")
