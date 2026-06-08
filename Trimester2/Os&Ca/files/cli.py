"""
MIT102 Assessment 2 — Memory Manager CLI
Interactive testing interface (system calls allowed here).
"""

import sys
from memory_manager import MemoryManager, PAGE_SIZE, NUM_FRAMES, PHYSICAL_MEMORY

HELP_TEXT = """
Available Commands
──────────────────────────────────────────────────────────
  create  <name>                 Create a new process
  term    <pid>                  Terminate a process
  alloc   <pid> <pages>          Allocate N pages for a process
  read    <pid> <hex_addr>       Read byte at logical address
  write   <pid> <hex_addr> <val> Write byte (0-255) to logical address
  pt      <pid>                  Dump page table for a process
  status                         Show full memory manager status
  help                           Show this help text
  quit / exit                    Exit the program
──────────────────────────────────────────────────────────
Addresses are in hex (e.g. 0x1000 or 1000).
"""


def parse_addr(s: str) -> int:
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    try:
        return int(s, 16)
    except ValueError:
        return int(s)


def run_cli():
    mm = MemoryManager()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  MIT102 — Memory Manager   (LRU Page Replacement)   ║")
    print(f"║  Physical: {PHYSICAL_MEMORY // 1024:>5} KB  |  {NUM_FRAMES} frames of {PAGE_SIZE} B       ║")
    print("║  Backing Store: 64 MB  |  Page size: 4 KB           ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(HELP_TEXT)

    while True:
        try:
            line = input("mm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not line or line.startswith("#"):
            continue

        parts = line.split()
        cmd   = parts[0].lower()

        try:
            if cmd in ("quit", "exit", "q"):
                print("Goodbye.")
                break

            elif cmd == "help":
                print(HELP_TEXT)

            elif cmd == "status":
                mm.status()

            elif cmd == "create":
                name = parts[1] if len(parts) > 1 else ""
                pid  = mm.create_process(name)
                print(f"  → Created PID={pid}")

            elif cmd == "term":
                if len(parts) < 2:
                    print("Usage: term <pid>")
                    continue
                mm.terminate_process(int(parts[1]))

            elif cmd == "alloc":
                if len(parts) < 3:
                    print("Usage: alloc <pid> <pages>")
                    continue
                start = mm.allocate_pages(int(parts[1]), int(parts[2]))
                print(f"  → Allocated, starting VPN={start}  logical addr=0x{start * PAGE_SIZE:08X}")

            elif cmd == "read":
                if len(parts) < 3:
                    print("Usage: read <pid> <hex_addr>")
                    continue
                mm.read(int(parts[1]), parse_addr(parts[2]))

            elif cmd == "write":
                if len(parts) < 4:
                    print("Usage: write <pid> <hex_addr> <value>")
                    continue
                mm.write(int(parts[1]), parse_addr(parts[2]), int(parts[3]))

            elif cmd == "pt":
                if len(parts) < 2:
                    print("Usage: pt <pid>")
                    continue
                mm.dump_page_table(int(parts[1]))

            else:
                print(f"Unknown command '{cmd}'. Type 'help' for options.")

        except (ValueError, MemoryError, IndexError) as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    run_cli()
