# MIT102 — Memory Manager
**Assessment 2: Programming Project**  
Unit: MIT102 Operating Systems and Computer Architecture  
Language: Python 3  
Page Replacement: LRU (Least Recently Used)

---

## Overview

This project simulates a paged memory management system with:

- **1 MB physical memory** — 256 frames of 4 KB each
- **64 MB backing store** — 16,384 swap slots of 4 KB each
- **LRU page replacement** — immune to Belady's Anomaly
- **Demand paging** — pages only load into RAM on first access
- **Dirty bit write-back** — only modified pages are written to backing store on eviction

---

## Files

| File | Description |
|---|---|
| `memory_manager.py` | Core engine — all memory logic, no system calls |
| `cli.py` | Interactive command-line interface for manual testing |
| `tests.py` | Automated test suite — 10 annotated test cases |
| `README.md` | This file |

---

## Requirements

- Python 3.6 or higher
- No external libraries required

---

## How to Run

### 1. Automated Tests

Runs all 10 test cases and prints a pass/fail summary.

```
python tests.py
```

### 2. Interactive CLI

Opens a prompt where you can manually issue memory manager commands.

```
python cli.py
```

---

## CLI Commands

| Command | Description | Example |
|---|---|---|
| `create <name>` | Create a new process | `create Alpha` |
| `alloc <pid> <pages>` | Allocate N virtual pages | `alloc 1 4` |
| `write <pid> <addr> <val>` | Write a byte (0–255) to a logical address | `write 1 0x1000 255` |
| `read <pid> <addr>` | Read a byte from a logical address | `read 1 0x1000` |
| `pt <pid>` | Print the page table for a process | `pt 1` |
| `status` | Show full memory manager status | `status` |
| `term <pid>` | Terminate a process and free its frames | `term 1` |
| `help` | Show all commands | `help` |
| `quit` | Exit the CLI | `quit` |

> Addresses can be written in hex with or without the `0x` prefix (e.g. `0x1000` or `1000`).

---

## Example Session

```
mm> create Alpha
[CREATE] PID=1 name='Alpha' — page table allocated (1024 entries)
  → Created PID=1

mm> alloc 1 3
[ALLOC] PID=1 3 pages starting at VPN=0 (demand-paged to backing store)

mm> write 1 0x0000 42
  → PAGE FAULT  PID=1 VPN=0  → loaded to frame 0
[WRITE] PID=1 addr=0x00000000  vpn=0 off=0  frame=0  value=0x2A

mm> read 1 0x0000
[READ]  PID=1 addr=0x00000000  vpn=0 off=0  frame=0  value=0x2A

mm> status
============================================================
  MEMORY MANAGER STATUS
============================================================
  Physical Frames :  256  (1024 KB)
  Used Frames     :    1
  Free Frames     :  255
  Page Faults     :    1
  Evictions       :    0
  Swap-Outs       :    0
  Swap-Ins        :    1
  Active Processes:    1
------------------------------------------------------------
  PID= 1  Alpha                 RAM=   1  DISK=   2
============================================================

mm> quit
```

---

## System Design Summary

| Parameter | Value |
|---|---|
| Physical Memory | 1 MB |
| Backing Store | 64 MB |
| Page Size | 4 KB |
| Physical Frames | 256 |
| Backing Frames | 16,384 |
| Max Processes | 16 |
| Logical Space / Process | 4 MB (1,024 virtual pages) |
| Page Replacement | LRU |

---

## Page States

| State | Meaning |
|---|---|
| `INVALID` | Page never allocated — auto-allocated on first access |
| `DISK` | Allocated but not in RAM — triggers a page fault on access |
| `RAM` | In physical memory — served directly |
| `FREE` | Released after process termination |

---

## Test Cases

| # | Test | What It Checks |
|---|---|---|
| 1 | Process Creation | Sequential PIDs, independent page tables |
| 2 | Page Allocation | Demand paging — no physical frame used until first access |
| 3 | Write → Page Fault | Page fault fires on first write; page moves to RAM |
| 4 | Read → Page Hit | No fault on re-reading a loaded page; correct value returned |
| 5 | Cross-page R/W | Correct values across multiple virtual pages |
| 6 | Auto-Allocation | INVALID page auto-allocated and loaded on first access |
| 7 | LRU Eviction | LRU eviction fires correctly when all 256 frames are full |
| 8 | Dirty Write-Back | Modified pages written to backing store on eviction |
| 9 | Termination | All frames freed correctly when a process terminates |
| 10 | Max Process Limit | MemoryError raised on 17th process creation |
