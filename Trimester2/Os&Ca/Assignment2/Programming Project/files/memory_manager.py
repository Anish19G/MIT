"""
MIT102 - Operating Systems and Computer Architecture
Assessment 2: Memory Manager with LRU Page Replacement

Design Decisions:
  - Physical Memory : 1 MB  (1,048,576 bytes)
  - Backing Store   : 64 MB (67,108,864 bytes)
  - Page Size       : 4 KB  (4,096 bytes)  [max allowed]
  - Physical Frames : 1 MB / 4 KB = 256 frames
  - Backing Frames  : 64 MB / 4 KB = 16,384 frames
  - Max Processes   : 16 (page table limit)
  - Logical Limit   : 4 MB per process (1,024 virtual pages per process)
  - Page Replacement: LRU (Least Recently Used) — immune to Belady's Anomaly
"""

import time
import collections
from dataclasses import dataclass, field
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────
PAGE_SIZE        = 4096          # 4 KB
PHYSICAL_MEMORY  = 1 * 1024 * 1024   # 1 MB
BACKING_STORE    = 64 * 1024 * 1024  # 64 MB
NUM_FRAMES       = PHYSICAL_MEMORY // PAGE_SIZE    # 256 physical frames
NUM_BACK_FRAMES  = BACKING_STORE // PAGE_SIZE      # 16,384 backing frames
MAX_PROCESSES    = 16
PAGES_PER_PROC   = 1024          # 4 MB logical space per process

# ─── Page States ──────────────────────────────────────────────────────────────
STATE_FREE    = "FREE"     # Page not allocated
STATE_RAM     = "RAM"      # Page in physical memory
STATE_DISK    = "DISK"     # Page swapped to backing store
STATE_INVALID = "INVALID"  # Page not yet allocated by process


# ─── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class PageTableEntry:
    """
    One row in a process's page table.
    Maps a virtual page number → physical frame (or backing frame).
    """
    state        : str  = STATE_INVALID  # FREE / RAM / DISK / INVALID
    frame_number : int  = -1             # physical frame if RAM, backing frame if DISK
    dirty        : bool = False          # has page been written to?
    referenced   : bool = False          # recently accessed?


@dataclass
class FrameInfo:
    """Tracks what is occupying each physical frame."""
    pid        : int = -1    # owning process (-1 = free)
    vpn        : int = -1    # virtual page number occupying this frame
    last_used  : int = 0     # timestamp for LRU


class PhysicalMemory:
    """Manages the 256 physical frames."""

    def __init__(self):
        self.frames: list[FrameInfo] = [FrameInfo() for _ in range(NUM_FRAMES)]
        self.free_frames: list[int] = list(range(NUM_FRAMES))
        self.page_faults   = 0
        self.page_evictions = 0
        self._clock = 0      # logical clock for LRU timestamps

    def tick(self) -> int:
        self._clock += 1
        return self._clock

    def allocate_frame(self) -> Optional[int]:
        """Return a free frame number, or None if memory is full."""
        if self.free_frames:
            return self.free_frames.pop(0)
        return None

    def free_frame(self, frame_no: int):
        self.frames[frame_no] = FrameInfo()
        self.free_frames.append(frame_no)

    def lru_victim(self) -> int:
        """
        Find the physical frame with the smallest last_used timestamp (LRU).
        LRU is Belady's-Anomaly-free for stack algorithms.
        """
        occupied = [(i, f) for i, f in enumerate(self.frames) if f.pid != -1]
        victim_frame, _ = min(occupied, key=lambda x: x[1].last_used)
        return victim_frame

    def touch_frame(self, frame_no: int):
        """Update LRU timestamp."""
        self.frames[frame_no].last_used = self.tick()

    @property
    def used_frames(self) -> int:
        return NUM_FRAMES - len(self.free_frames)

    @property
    def free_frame_count(self) -> int:
        return len(self.free_frames)


class BackingStore:
    """Simulates 64 MB backing store (swap space) — stored in a Python dict."""

    def __init__(self):
        # backing_frame_no → bytearray (page content)
        self._store: dict[int, bytearray] = {}
        self._free: list[int] = list(range(NUM_BACK_FRAMES))
        self.swap_ins  = 0
        self.swap_outs = 0

    def allocate_frame(self) -> Optional[int]:
        if self._free:
            return self._free.pop(0)
        return None

    def free_frame(self, bframe: int):
        if bframe in self._store:
            del self._store[bframe]
        self._free.append(bframe)

    def write(self, bframe: int, data: bytearray):
        self._store[bframe] = bytearray(data)
        self.swap_outs += 1

    def read(self, bframe: int) -> bytearray:
        self.swap_ins += 1
        return bytearray(self._store.get(bframe, bytearray(PAGE_SIZE)))


# ─── Memory Manager ───────────────────────────────────────────────────────────

class MemoryManager:
    """
    Top-level memory manager.

    Physical memory: 1 MB / 256 frames of 4 KB each.
    Backing store  : 64 MB / 16,384 frames of 4 KB each.
    Page replacement: LRU (no Belady's Anomaly).
    """

    def __init__(self):
        self.phys_mem    = PhysicalMemory()
        self.back_store  = BackingStore()

        # page_tables[pid][vpn] = PageTableEntry
        self.page_tables : dict[int, list[PageTableEntry]] = {}

        # physical_memory_data[frame_no] = bytearray(PAGE_SIZE)
        self.phys_data   : list[bytearray] = [bytearray(PAGE_SIZE) for _ in range(NUM_FRAMES)]

        self.processes   : dict[int, str] = {}   # pid → process name
        self._next_pid   = 1

    # ── Process Lifecycle ─────────────────────────────────────────────────────

    def create_process(self, name: str = "") -> int:
        """Allocate a new process; return its PID."""
        if len(self.processes) >= MAX_PROCESSES:
            raise MemoryError("Maximum process limit reached.")
        pid = self._next_pid
        self._next_pid += 1
        self.processes[pid] = name or f"Process-{pid}"
        self.page_tables[pid] = [PageTableEntry() for _ in range(PAGES_PER_PROC)]
        print(f"[CREATE] PID={pid} name='{self.processes[pid]}' — page table allocated ({PAGES_PER_PROC} entries)")
        return pid

    def terminate_process(self, pid: int):
        """Free all physical and backing-store frames owned by a process."""
        self._require_pid(pid)
        freed_physical = 0
        freed_backing  = 0
        for vpn, pte in enumerate(self.page_tables[pid]):
            if pte.state == STATE_RAM:
                self.phys_mem.free_frame(pte.frame_number)
                freed_physical += 1
            elif pte.state == STATE_DISK:
                self.back_store.free_frame(pte.frame_number)
                freed_backing += 1
        del self.page_tables[pid]
        del self.processes[pid]
        print(f"[TERMINATE] PID={pid} freed {freed_physical} physical + {freed_backing} backing frames")

    # ── Memory Access ─────────────────────────────────────────────────────────

    def read(self, pid: int, logical_addr: int) -> int:
        """Read one byte from a logical address. Returns the byte value."""
        self._require_pid(pid)
        vpn, offset = divmod(logical_addr, PAGE_SIZE)
        self._validate_vpn(vpn)
        frame = self._access_page(pid, vpn, write=False)
        value = self.phys_data[frame][offset]
        print(f"[READ]  PID={pid} addr=0x{logical_addr:08X}  vpn={vpn} off={offset}  frame={frame}  value=0x{value:02X}")
        return value

    def write(self, pid: int, logical_addr: int, value: int):
        """Write one byte to a logical address."""
        self._require_pid(pid)
        vpn, offset = divmod(logical_addr, PAGE_SIZE)
        self._validate_vpn(vpn)
        frame = self._access_page(pid, vpn, write=True)
        self.phys_data[frame][offset] = value & 0xFF
        print(f"[WRITE] PID={pid} addr=0x{logical_addr:08X}  vpn={vpn} off={offset}  frame={frame}  value=0x{value & 0xFF:02X}")

    def allocate_pages(self, pid: int, num_pages: int) -> int:
        """
        Lazily mark `num_pages` virtual pages as DISK-allocated (demand paging).
        Returns the starting virtual page number.
        """
        self._require_pid(pid)
        pt = self.page_tables[pid]
        start_vpn = -1
        allocated = 0
        for vpn, pte in enumerate(pt):
            if pte.state == STATE_INVALID:
                if start_vpn == -1:
                    start_vpn = vpn
                bframe = self.back_store.allocate_frame()
                if bframe is None:
                    raise MemoryError("Backing store is full.")
                pte.state        = STATE_DISK
                pte.frame_number = bframe
                allocated += 1
                if allocated == num_pages:
                    break
        if allocated < num_pages:
            raise MemoryError(f"Could only allocate {allocated}/{num_pages} pages.")
        print(f"[ALLOC] PID={pid} {num_pages} pages starting at VPN={start_vpn} (demand-paged to backing store)")
        return start_vpn

    # ── Page Fault Handler ────────────────────────────────────────────────────

    def _access_page(self, pid: int, vpn: int, write: bool) -> int:
        """
        Translate VPN → physical frame.
        Triggers a page fault (and LRU eviction if needed) when the page is not in RAM.
        Returns the physical frame number.
        """
        pte = self.page_tables[pid][vpn]

        # Auto-allocate on first access if page was never explicitly allocated
        if pte.state == STATE_INVALID:
            bframe = self.back_store.allocate_frame()
            if bframe is None:
                raise MemoryError("Backing store full during auto-allocation.")
            pte.state        = STATE_DISK
            pte.frame_number = bframe

        if pte.state == STATE_RAM:
            # Page hit — just update LRU timestamp
            self.phys_mem.touch_frame(pte.frame_number)
            if write:
                pte.dirty = True
            return pte.frame_number

        # ── Page Fault ────────────────────────────────────────────────────────
        self.phys_mem.page_faults += 1
        print(f"  → PAGE FAULT  PID={pid} VPN={vpn}", end="")

        frame = self.phys_mem.allocate_frame()

        if frame is None:
            # No free frame — LRU eviction
            frame = self.phys_mem.lru_victim()
            victim_info = self.phys_mem.frames[frame]
            v_pid, v_vpn = victim_info.pid, victim_info.vpn
            victim_pte   = self.page_tables[v_pid][v_vpn]

            if victim_pte.dirty:
                # Write-back dirty page to backing store
                self.back_store.write(victim_pte.frame_number, self.phys_data[frame])
                print(f"  [EVICT-DIRTY] PID={v_pid} VPN={v_vpn} frame={frame}", end="")
            else:
                print(f"  [EVICT-CLEAN] PID={v_pid} VPN={v_vpn} frame={frame}", end="")

            victim_pte.state = STATE_DISK
            victim_pte.dirty = False
            self.phys_mem.page_evictions += 1

        # Load page from backing store into physical frame
        if pte.state == STATE_DISK:
            self.phys_data[frame] = self.back_store.read(pte.frame_number)

        # Update page table entry
        pte.state        = STATE_RAM
        pte.frame_number = frame
        if write:
            pte.dirty = True

        # Update frame table
        fi = self.phys_mem.frames[frame]
        fi.pid = pid
        fi.vpn = vpn
        self.phys_mem.touch_frame(frame)

        print(f"  → loaded to frame {frame}")
        return frame

    # ── Status / Reporting ────────────────────────────────────────────────────

    def status(self):
        print("\n" + "=" * 60)
        print("  MEMORY MANAGER STATUS")
        print("=" * 60)
        print(f"  Physical Frames : {NUM_FRAMES}  ({PHYSICAL_MEMORY // 1024} KB)")
        print(f"  Used Frames     : {self.phys_mem.used_frames}")
        print(f"  Free Frames     : {self.phys_mem.free_frame_count}")
        print(f"  Page Faults     : {self.phys_mem.page_faults}")
        print(f"  Evictions       : {self.phys_mem.page_evictions}")
        print(f"  Swap-Outs       : {self.back_store.swap_outs}")
        print(f"  Swap-Ins        : {self.back_store.swap_ins}")
        print(f"  Active Processes: {len(self.processes)}")
        print("-" * 60)
        for pid, name in self.processes.items():
            pt = self.page_tables[pid]
            in_ram  = sum(1 for p in pt if p.state == STATE_RAM)
            on_disk = sum(1 for p in pt if p.state == STATE_DISK)
            print(f"  PID={pid:2d}  {name:<20s}  RAM={in_ram:4d}  DISK={on_disk:4d}")
        print("=" * 60 + "\n")

    def dump_page_table(self, pid: int):
        self._require_pid(pid)
        pt = self.page_tables[pid]
        print(f"\n--- Page Table  PID={pid}  ({self.processes[pid]}) ---")
        print(f"{'VPN':>6}  {'State':<8}  {'Frame':>6}  {'Dirty':<5}  {'Ref':<5}")
        print("-" * 40)
        for vpn, pte in enumerate(pt):
            if pte.state != STATE_INVALID:
                print(f"{vpn:6d}  {pte.state:<8}  {pte.frame_number:6d}  {str(pte.dirty):<5}  {str(pte.referenced):<5}")
        print()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _require_pid(self, pid: int):
        if pid not in self.processes:
            raise ValueError(f"PID {pid} does not exist.")

    @staticmethod
    def _validate_vpn(vpn: int):
        if not (0 <= vpn < PAGES_PER_PROC):
            raise ValueError(f"VPN {vpn} out of range (max {PAGES_PER_PROC - 1}).")
