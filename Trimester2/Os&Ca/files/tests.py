"""
MIT102 Assessment 2 — Test Suite
Exercises all memory manager functionality and records annotated results.
"""

import sys
import io
import contextlib
from memory_manager import MemoryManager, PAGE_SIZE, NUM_FRAMES


def header(title: str):
    print("\n" + "═" * 60)
    print(f"  TEST: {title}")
    print("═" * 60)


def annotation(text: str):
    print(f"\n  ✦ {text}")


def run_tests():
    results = []

    # ── Test 1: Process Creation ───────────────────────────────────────────────
    header("Process Creation")
    mm = MemoryManager()
    annotation("Create three processes; each gets its own page table.")
    p1 = mm.create_process("Alpha")
    p2 = mm.create_process("Beta")
    p3 = mm.create_process("Gamma")
    assert p1 == 1 and p2 == 2 and p3 == 3, "PIDs should be sequential"
    assert len(mm.processes) == 3
    annotation("PASS — three processes created, PIDs 1/2/3.")
    results.append(("Process Creation", True))

    # ── Test 2: Explicit Page Allocation ──────────────────────────────────────
    header("Explicit Page Allocation")
    annotation("Allocate 4 pages for P1 and 2 pages for P2 (demand paging).")
    start1 = mm.allocate_pages(p1, 4)
    start2 = mm.allocate_pages(p2, 2)
    assert start1 == 0, "First allocation must start at VPN 0"
    assert start2 == 0
    annotation("Pages allocated to backing store (not in RAM yet — demand paging).")
    pt1 = mm.page_tables[p1]
    from memory_manager import STATE_DISK, STATE_INVALID
    assert all(pt1[v].state == STATE_DISK for v in range(4))
    assert all(pt1[v].state == STATE_INVALID for v in range(4, 10))
    annotation("PASS — pages 0-3 of P1 are DISK-resident; rest INVALID.")
    results.append(("Page Allocation", True))

    # ── Test 3: Write triggers page fault + load ───────────────────────────────
    header("Write → Page Fault → Load from Backing Store")
    annotation("First write to logical address 0x0000 (P1, VPN=0) triggers a page fault.")
    initial_faults = mm.phys_mem.page_faults
    mm.write(p1, 0x0000, 0xAB)
    assert mm.phys_mem.page_faults == initial_faults + 1, "One page fault expected"
    from memory_manager import STATE_RAM
    assert mm.page_tables[p1][0].state == STATE_RAM, "Page should now be in RAM"
    annotation("PASS — page fault fired, page loaded to physical memory.")
    results.append(("Write → Page Fault", True))

    # ── Test 4: Read same page (page hit, no fault) ────────────────────────────
    header("Read same page — Page Hit (no fault)")
    annotation("Reading the same page should NOT cause another page fault.")
    faults_before = mm.phys_mem.page_faults
    val = mm.read(p1, 0x0000)
    assert mm.phys_mem.page_faults == faults_before, "No new page fault on hit"
    assert val == 0xAB, f"Expected 0xAB, got 0x{val:02X}"
    annotation(f"PASS — page hit, read back value 0x{val:02X} correctly.")
    results.append(("Read → Page Hit", True))

    # ── Test 5: Write/Read across page boundary ────────────────────────────────
    header("Write and Read Across Multiple Pages")
    annotation("Write to the last byte of VPN=1 and first byte of VPN=2.")
    mm.write(p1, 1 * PAGE_SIZE - 1, 0x11)   # last byte of VPN=0
    mm.write(p1, 1 * PAGE_SIZE,     0x22)   # first byte of VPN=1
    mm.write(p1, 2 * PAGE_SIZE,     0x33)   # first byte of VPN=2
    v0 = mm.read(p1, 1 * PAGE_SIZE - 1)
    v1 = mm.read(p1, 1 * PAGE_SIZE)
    v2 = mm.read(p1, 2 * PAGE_SIZE)
    assert v0 == 0x11 and v1 == 0x22 and v2 == 0x33
    annotation("PASS — correct values read back from three different pages.")
    results.append(("Cross-page R/W", True))

    # ── Test 6: Auto-allocation (INVALID page accessed) ───────────────────────
    header("Auto-Allocation on INVALID Page Access")
    annotation("P3 has no explicit allocations; first access auto-allocates.")
    faults_pre = mm.phys_mem.page_faults
    mm.write(p3, 0x5000, 0xFF)  # VPN=5 for P3, never allocated
    assert mm.phys_mem.page_faults > faults_pre
    assert mm.page_tables[p3][5].state == STATE_RAM
    annotation("PASS — INVALID page auto-allocated and brought into RAM.")
    results.append(("Auto-Allocation", True))

    # ── Test 7: LRU Eviction ──────────────────────────────────────────────────
    header("LRU Page Eviction (fill all physical frames)")
    annotation(f"Fill all {NUM_FRAMES} physical frames, then force an eviction.")
    mm2 = MemoryManager()
    pid = mm2.create_process("Filler")
    # Touch NUM_FRAMES distinct pages to fill RAM
    evictions_before = mm2.phys_mem.page_evictions
    for vpn in range(NUM_FRAMES):
        mm2.write(pid, vpn * PAGE_SIZE, vpn & 0xFF)
    assert mm2.phys_mem.used_frames == NUM_FRAMES, "All frames should be full"
    annotation(f"All {NUM_FRAMES} frames filled. Now accessing one more page to trigger LRU eviction.")
    mm2.write(pid, NUM_FRAMES * PAGE_SIZE, 0xEE)  # one beyond — must evict
    assert mm2.phys_mem.page_evictions > evictions_before, "LRU eviction must have occurred"
    annotation(f"PASS — LRU eviction fired (total evictions: {mm2.phys_mem.page_evictions}).")
    results.append(("LRU Eviction", True))

    # ── Test 8: Dirty page write-back ─────────────────────────────────────────
    header("Dirty Page Write-Back on Eviction")
    annotation("Verify that a written (dirty) page is saved to backing store on eviction.")
    mm3 = MemoryManager()
    px = mm3.create_process("DirtyTest")
    for vpn in range(NUM_FRAMES):
        mm3.write(px, vpn * PAGE_SIZE, 0xCC)   # fill RAM, all dirty
    swaps_before = mm3.back_store.swap_outs
    mm3.write(px, NUM_FRAMES * PAGE_SIZE, 0xDD)  # force eviction of dirty page
    assert mm3.back_store.swap_outs > swaps_before, "Dirty page must be written to backing store"
    annotation(f"PASS — dirty page flushed (swap-outs: {mm3.back_store.swap_outs}).")
    results.append(("Dirty Write-Back", True))

    # ── Test 9: Process Termination frees frames ──────────────────────────────
    header("Process Termination Frees Physical Frames")
    annotation("Terminate P1 and verify all its frames are returned to the free pool.")
    mm4 = MemoryManager()
    pa = mm4.create_process("Termination")
    for vpn in range(5):
        mm4.write(pa, vpn * PAGE_SIZE, vpn)
    frames_before = mm4.phys_mem.free_frame_count
    mm4.terminate_process(pa)
    assert mm4.phys_mem.free_frame_count > frames_before
    assert pa not in mm4.processes
    annotation(f"PASS — freed {mm4.phys_mem.free_frame_count - frames_before} frames on termination.")
    results.append(("Termination", True))

    # ── Test 10: Max process limit ────────────────────────────────────────────
    header("Max Process Limit (16 processes)")
    annotation("Creating more than 16 processes should raise MemoryError.")
    mm5 = MemoryManager()
    for i in range(16):
        mm5.create_process(f"P{i}")
    try:
        mm5.create_process("overflow")
        annotation("FAIL — should have raised MemoryError!")
        results.append(("Max Process Limit", False))
    except MemoryError:
        annotation("PASS — MemoryError raised correctly at 17th process.")
        results.append(("Max Process Limit", True))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  TEST RESULTS SUMMARY")
    print("═" * 60)
    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        mark = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {mark}  {name}")
    print(f"\n  {passed}/{len(results)} tests passed.")
    print("═" * 60 + "\n")

    mm.status()
    mm.dump_page_table(p1)


if __name__ == "__main__":
    run_tests()
