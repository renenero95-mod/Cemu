P = "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanRenderer.cpp"
c = open(P).read()

# 1. Timer AcquireNextSwapchainImage
old1 = "\tif(!AcquireNextSwapchainImage(mainWindow))\n\t\treturn;"
new1 = "\tauto tAcq = std::chrono::steady_clock::now();\n\tbool acqOk = AcquireNextSwapchainImage(mainWindow);\n\tauto acqMs = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - tAcq).count();\n\tif (acqMs > 50) cemuLog_log(LogType::Force, \"[PRESENT SLOW] Acquire={}ms\", acqMs);\n\tif(!acqOk)\n\t\treturn;"
assert c.count(old1) >= 1, "acq anchor"
# Sostituisci solo la prima occorrenza (in SwapBuffer)
c = c.replace(old1, new1, 1)

# 2. Timer chainInfo.WaitAvailableFence
old2 = "\tchainInfo.WaitAvailableFence();"
new2 = "\tauto tFence = std::chrono::steady_clock::now();\n\tchainInfo.WaitAvailableFence();\n\tauto fenceMs = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - tFence).count();\n\tif (fenceMs > 50) cemuLog_log(LogType::Force, \"[PRESENT SLOW] ChainFence={}ms\", fenceMs);"
assert c.count(old2) >= 1, "fence anchor"
c = c.replace(old2, new2, 1)

# 3. Timer WaitCommandBufferFinished (in SwapBuffer)
old3 = "\tWaitCommandBufferFinished(m_commandBufferIDOfPrevFrame);"
new3 = "\tauto tWait = std::chrono::steady_clock::now();\n\tWaitCommandBufferFinished(m_commandBufferIDOfPrevFrame);\n\tauto waitMs = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - tWait).count();\n\tif (waitMs > 50) cemuLog_log(LogType::Force, \"[PRESENT SLOW] CmdBufFinish={}ms\", waitMs);"
assert c.count(old3) >= 1, "wait anchor"
c = c.replace(old3, new3, 1)

open(P, "w").write(c)
print("[OK] 3 timer aggiunti al present path")
