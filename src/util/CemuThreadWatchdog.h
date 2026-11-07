#pragma once

#ifndef CEMU_THREAD_WATCHDOG
#define CEMU_THREAD_WATCHDOG 1
#endif

#if CEMU_THREAD_WATCHDOG

#include <atomic>
#include <chrono>
#include <cstdint>
#include <thread>
#include <exception>

namespace CemuWatchdog
{
    using Clock = std::chrono::steady_clock;

    enum ThreadId : uint32_t
    {
        Main = 0,
        Renderer = 1,
        Recompiler = 2
    };

    enum Phase : uint32_t
    {
        Loop = 0,
        Sleep = 1,
        QueueWait = 2,
        FenceWait = 3,
        Present = 4,
        Compile = 5
    };

    struct State
    {
        std::atomic<uint64_t> lastNs{ 0 };
        std::atomic<uint64_t> ticks{ 0 };
        std::atomic<uint32_t> phase{ Loop };
    };

    inline State& GetState(ThreadId id)
    {
        static State states[3];
        return states[static_cast<uint32_t>(id)];
    }

    inline uint64_t NowNs()
    {
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                Clock::now().time_since_epoch()).count());
    }

    inline void Touch(ThreadId id, Phase phase)
    {
        State& s = GetState(id);
        s.phase.store(phase, std::memory_order_relaxed);
        s.lastNs.store(NowNs(), std::memory_order_relaxed);
        s.ticks.fetch_add(1, std::memory_order_relaxed);
    }

    inline bool Start()
    {
        static std::atomic<bool> started{ false };

        if (started.exchange(true, std::memory_order_relaxed))
            return false;

        cemuLog_log(LogType::Force, "[WATCHDOG START] Start() invoked");

        const uint64_t now = NowNs();

        for (uint32_t i = 0; i < 3; ++i)
        {
            GetState(static_cast<ThreadId>(i)).lastNs.store(
                now, std::memory_order_relaxed);
        }

        try
        {
            std::thread([]()
            {
                cemuLog_log(LogType::Force, "[WATCHDOG THREAD] worker started");
                uint64_t reportCount = 0;

                for (;;)
                {
                    std::this_thread::sleep_for(std::chrono::seconds(2));
                    const uint64_t now = NowNs();
                    
                    cemuLog_log(LogType::Force, "[WATCHDOG ALIVE] report={}", ++reportCount);

                    for (uint32_t i = 0; i < 3; ++i)
                    {
                        const State& s = GetState(static_cast<ThreadId>(i));
                        const uint64_t last = s.lastNs.load(std::memory_order_relaxed);
                        const uint64_t ageMs = last == 0 ? 0 : (now - last) / 1000000ULL;
                        const uint64_t ticks = s.ticks.load(std::memory_order_relaxed);
                        const uint32_t phase = s.phase.load(std::memory_order_relaxed);

                        cemuLog_log(LogType::Force, "[THREAD WATCH] id={} phase={} age={}ms ticks={}", i, phase, ageMs, ticks);
                    }
                }
            }).detach();

            cemuLog_log(LogType::Force, "[WATCHDOG START] worker thread created");
            return true;
        }
        catch (const std::exception& e)
        {
            cemuLog_log(LogType::Force, "[WATCHDOG ERROR] thread creation failed: {}", e.what());
            return false;
        }
    }
}

#endif
