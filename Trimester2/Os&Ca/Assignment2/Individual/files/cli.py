"""
MIT102 Assessment 3 — Hash Table Interactive CLI
System calls (input, print) are allowed here.
"""

from hash_table import HashTable

HELP = """
Commands
──────────────────────────────────────────────
  init   <buckets>          Initialise hash table
  insert <x>                Insert integer x
  remove <x>                Remove integer x
  count                     Total element count
  bucket <n>                Element count in bucket n
  dump                      Print full hash table
  help                      Show this help
  quit                      Exit
──────────────────────────────────────────────
"""

def run():
    ht = HashTable()
    print("MIT102 — Thread-Safe Hash Table CLI")
    print(HELP)

    while True:
        try:
            line = input("ht> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()

        try:
            if cmd in ("quit", "exit", "q"):
                print("Goodbye.")
                break
            elif cmd == "help":
                print(HELP)
            elif cmd == "init":
                ht.Hash_Init(int(parts[1]))
            elif cmd == "insert":
                r = ht.Hash_Insert(int(parts[1]))
                print("  Inserted." if r == 0 else "  Already exists (-1).")
            elif cmd == "remove":
                r = ht.Hash_Remove(int(parts[1]))
                print("  Removed." if r == 0 else "  Not found (-1).")
            elif cmd == "count":
                print(f"  Total elements: {ht.Hash_CountElements()}")
            elif cmd == "bucket":
                print(f"  Bucket {parts[1]} elements: {ht.Hash_CountBucketElements(int(parts[1]))}")
            elif cmd == "dump":
                ht.Hash_Dump()
            else:
                print(f"  Unknown command '{cmd}'. Type 'help'.")
        except (IndexError, ValueError) as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    run()
