#pragma once

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <map>
#include <mutex>
#include <utility>
#include <vector>

namespace CemuDiagV2
{
    extern std::atomic<uint64_t> g_jitCount;
    extern std::atomic<uint64_t> g_jitTotalNs;
    extern std::atomic<uint64_t> g_jitMaxNs;
    extern std::mutex g_jitTop5Mtx;
    extern std::map<uint32_t, uint64_t> g_jitTop5Map;

    extern std::atomic<uint64_t> g_vkDrawCount;
    extern std::atomic<uint64_t> g_vkSubmitCount;
    extern std::atomic<uint64_t> g_vkSubmitNs;
    extern std::atomic<uint64_t> g_vkPresentCount;
    extern std::atomic<uint64_t> g_vkPresentNs;

    class ScopedJitTimer
    {
    public:
        explicit ScopedJitTimer(uint32_t ppcAddress)
            : m_ppcAddress(ppcAddress), m_start(std::chrono::steady_clock::now()) {}

        ~ScopedJitTimer()
        {
            const auto elapsedNs = std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::steady_clock::now() - m_start).count();
            const uint64_t ns = static_cast<uint64_t>(elapsedNs);
            g_jitCount.fetch_add(1, std::memory_order_relaxed);
            g_jitTotalNs.fetch_add(ns, std::memory_order_relaxed);
            uint64_t prevMax = g_jitMaxNs.load(std::memory_order_relaxed);
            while (ns > prevMax && !g_jitMaxNs.compare_exchange_weak(
                       prevMax, ns, std::memory_order_relaxed)) {}
            {
                std::lock_guard<std::mutex> lock(g_jitTop5Mtx);
                g_jitTop5Map[m_ppcAddress]++;
            }
        }

        ScopedJitTimer(const ScopedJitTimer&) = delete;
        ScopedJitTimer& operator=(const ScopedJitTimer&) = delete;

    private:
        uint32_t m_ppcAddress;
        std::chrono::steady_clock::time_point m_start;
    };
}
