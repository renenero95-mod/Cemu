#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <cstdint>

namespace PPCPreExecutionAnalyzer {
    struct InstructionMetadata {
        uint32_t guestPc;
        uint32_t rawOpcode;
        uint8_t primaryOpcode;
        uint16_t secondaryOpcode;
    };

    void ScanExecutableSection(uint32_t guestBase, const uint8_t* bytes, size_t size, const std::string& moduleName);
    void InvalidateRange(uint32_t guestStart, uint32_t guestEnd);
    void ClearTitle();
    bool Lookup(uint32_t guestPc, InstructionMetadata& out);
}
