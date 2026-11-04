#pragma once

#ifndef CEMU_PROFILING
#define CEMU_PROFILING 1
#endif

#if CEMU_PROFILING
#include <atomic>
#include <chrono>
#include <cstdint>

namespace CemuProfiling
{
    using Clock = std::chrono::steady_clock;

    struct Counter
    {
        std::atomic<uint64_t> calls{ 0 };
        std::atomic<uint64_t> items{ 0 };
        std::atomic<uint64_t> nanoseconds{ 0 };

        void Record(uint64_t itemCount, uint64_t elapsedNs)
        {
            calls.fetch_add(1, std::memory_order_relaxed);
            items.fetch_add(itemCount, std::memory_order_relaxed);
            nanoseconds.fetch_add(elapsedNs, std::memory_order_relaxed);
        }

        void AddItems(uint64_t itemCount = 1)
        {
            items.fetch_add(itemCount, std::memory_order_relaxed);
        }

        struct Snapshot
        {
            uint64_t calls;
            uint64_t items;
            uint64_t nanoseconds;
        };

        Snapshot TakeSnapshot()
        {
            return {
                calls.exchange(0, std::memory_order_relaxed),
                items.exchange(0, std::memory_order_relaxed),
                nanoseconds.exchange(0, std::memory_order_relaxed)
            };
        }
    };

    inline Counter& Interpreter()       { static Counter c; return c; }
    inline Counter& HLE()               { static Counter c; return c; }
    inline Counter& Recompiler()        { static Counter c; return c; }
    inline Counter& FiberTimeslice()    { static Counter c; return c; }
    inline Counter& Drawcalls()         { static Counter c; return c; }
    inline Counter& PipelineChanges()   { static Counter c; return c; }
    inline Counter& ThreadSleepWait()   { static Counter c; return c; }
    inline Counter& ThreadJoinWait()    { static Counter c; return c; }
    inline Counter& ThreadQueueWait()   { static Counter c; return c; }
    inline Counter& VulkanSubmit()      { static Counter c; return c; }
    inline Counter& VulkanPresent()     { static Counter c; return c; }
    inline Counter& VulkanFenceWait()   { static Counter c; return c; }
    inline Counter& AudioUpdate()       { static Counter c; return c; }
    inline Counter& AudioMutexWait()    { static Counter c; return c; }

    class ScopedTimer
    {
    public:
        explicit ScopedTimer(Counter& counter, uint64_t itemCount = 1)
            : m_counter(counter), m_itemCount(itemCount), m_start(Clock::now())
        {
        }

        ~ScopedTimer()
        {
            const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(
                Clock::now() - m_start).count();
            m_counter.Record(m_itemCount, static_cast<uint64_t>(elapsed));
        }

        ScopedTimer(const ScopedTimer&) = delete;
        ScopedTimer& operator=(const ScopedTimer&) = delete;

    private:
        Counter& m_counter;
        uint64_t m_itemCount;
        Clock::time_point m_start;
    };

    inline uint64_t ElapsedNs(Clock::time_point start)
    {
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now() - start).count());
    }
}
#endif
