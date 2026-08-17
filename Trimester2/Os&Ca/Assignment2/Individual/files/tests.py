"""
MIT102 Assessment 3 — Thread-Safety Test Suite

Tests:
  1. Basic functionality (single-threaded)
  2. Concurrent inserts (many threads inserting simultaneously)
  3. Concurrent removes (many threads removing simultaneously)
  4. Mixed concurrent operations (insert + remove + count)
  5. Duplicate detection under concurrency
  6. Count accuracy under concurrent modifications
  7. Stress test (high thread count, many operations)

Each test compares the expected element count against Hash_CountElements().
"""

import threading
import random
import time
import sys
from hash_table import HashTable

PASS = "\u2713 PASS"
FAIL = "\u2717 FAIL"

results = []

def log(test_name, passed, detail=""):
    mark = PASS if passed else FAIL
    msg = f"  {mark}  {test_name}"
    if detail:
        msg += f"  [{detail}]"
    print(msg)
    results.append((test_name, passed))


def header(title):
    print(f"\n{'='*60}")
    print(f"  TEST: {title}")
    print(f"{'='*60}")


# ── Test 1: Basic Functionality ───────────────────────────────────────────────

def test_basic():
    header("Basic Functionality (single-threaded)")
    ht = HashTable()
    ht.Hash_Init(8)

    # Insert
    r = ht.Hash_Insert(10)
    log("Insert 10 returns 0", r == 0, f"got {r}")

    r = ht.Hash_Insert(10)
    log("Re-insert 10 returns -1 (duplicate)", r == -1, f"got {r}")

    ht.Hash_Insert(18)   # 18 % 8 == 2, same bucket as 10 % 8 == 2
    ht.Hash_Insert(5)
    ht.Hash_Insert(99)

    count = ht.Hash_CountElements()
    log("CountElements after 4 distinct inserts == 4", count == 4, f"got {count}")

    # Remove
    r = ht.Hash_Remove(5)
    log("Remove 5 returns 0", r == 0, f"got {r}")

    r = ht.Hash_Remove(5)
    log("Remove non-existent 5 returns -1", r == -1, f"got {r}")

    count = ht.Hash_CountElements()
    log("CountElements after remove == 3", count == 3, f"got {count}")

    # CountBucketElements
    bc = ht.Hash_CountBucketElements(2)   # 10 and 18 are in bucket 2
    log("CountBucketElements(2) == 2 (holds 10 and 18)", bc == 2, f"got {bc}")

    # Negative numbers
    ht.Hash_Insert(-7)
    r = ht.Hash_Remove(-7)
    log("Insert and remove negative number", r == 0, f"got {r}")

    # Zero
    ht.Hash_Insert(0)
    r = ht.Hash_Remove(0)
    log("Insert and remove zero", r == 0, f"got {r}")

    ht.Hash_Dump()


# ── Test 2: Concurrent Inserts ────────────────────────────────────────────────

def test_concurrent_inserts():
    header("Concurrent Inserts")
    NUM_THREADS = 20
    INSERTS_PER_THREAD = 50
    NUM_BUCKETS = 16

    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)

    # Each thread inserts a unique, non-overlapping range → no duplicates
    def worker(start):
        for i in range(start, start + INSERTS_PER_THREAD):
            ht.Hash_Insert(i)

    threads = [threading.Thread(target=worker, args=(t * INSERTS_PER_THREAD,))
               for t in range(NUM_THREADS)]
    for th in threads: th.start()
    for th in threads: th.join()

    expected = NUM_THREADS * INSERTS_PER_THREAD
    actual   = ht.Hash_CountElements()
    log(f"Concurrent inserts: expected={expected}, actual={actual}",
        actual == expected, f"got {actual}")


# ── Test 3: Concurrent Removes ────────────────────────────────────────────────

def test_concurrent_removes():
    header("Concurrent Removes")
    NUM_BUCKETS = 16
    TOTAL = 200

    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)
    for i in range(TOTAL):
        ht.Hash_Insert(i)

    NUM_THREADS = 20
    REMOVES_PER_THREAD = TOTAL // NUM_THREADS  # 10 each, all distinct

    def worker(start):
        for i in range(start, start + REMOVES_PER_THREAD):
            ht.Hash_Remove(i)

    threads = [threading.Thread(target=worker, args=(t * REMOVES_PER_THREAD,))
               for t in range(NUM_THREADS)]
    for th in threads: th.start()
    for th in threads: th.join()

    actual = ht.Hash_CountElements()
    log(f"Concurrent removes: expected=0, actual={actual}", actual == 0, f"got {actual}")


# ── Test 4: Mixed Concurrent Operations ───────────────────────────────────────

def test_mixed_concurrent():
    header("Mixed Concurrent Operations (insert + remove + count)")
    NUM_BUCKETS = 32
    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)

    # Pre-insert some values
    for i in range(100):
        ht.Hash_Insert(i)

    errors = []

    def inserter():
        for i in range(100, 200):
            ht.Hash_Insert(i)

    def remover():
        for i in range(0, 100):
            ht.Hash_Remove(i)

    def counter():
        for _ in range(50):
            c = ht.Hash_CountElements()
            if c < 0:
                errors.append(f"CountElements returned {c}")

    threads = (
        [threading.Thread(target=inserter) for _ in range(5)] +
        [threading.Thread(target=remover)  for _ in range(5)] +
        [threading.Thread(target=counter)  for _ in range(5)]
    )
    for th in threads: th.start()
    for th in threads: th.join()

    # After: 100–199 should be in, 0–99 removed
    final = ht.Hash_CountElements()
    log("Mixed ops: final count == 100 (values 100-199 remain)",
        final == 100, f"got {final}")
    log("No negative counts during concurrent reads", len(errors) == 0,
        f"{errors[:3]}" if errors else "")


# ── Test 5: Duplicate Detection Under Concurrency ─────────────────────────────

def test_concurrent_duplicates():
    header("Duplicate Detection Under Concurrency")
    NUM_BUCKETS = 8
    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)

    # All threads try to insert the same value
    SHARED_VALUE = 42
    NUM_THREADS  = 50
    insert_results = []
    lock = threading.Lock()

    def try_insert():
        r = ht.Hash_Insert(SHARED_VALUE)
        with lock:
            insert_results.append(r)

    threads = [threading.Thread(target=try_insert) for _ in range(NUM_THREADS)]
    for th in threads: th.start()
    for th in threads: th.join()

    successes = insert_results.count(0)
    duplicates = insert_results.count(-1)
    count = ht.Hash_CountElements()

    log("Only one insert succeeds (successes == 1)", successes == 1,
        f"successes={successes}")
    log(f"Remaining {NUM_THREADS-1} are duplicates", duplicates == NUM_THREADS - 1,
        f"duplicates={duplicates}")
    log("Hash table contains exactly 1 element", count == 1, f"got {count}")


# ── Test 6: Count Accuracy Under Concurrent Modifications ─────────────────────

def test_count_accuracy():
    header("Count Accuracy Under Concurrent Modifications")
    NUM_BUCKETS = 16
    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)

    # 10 inserter threads × 100 inserts each, unique values → 1000 total
    expected_inserted = 0
    insert_lock = threading.Lock()
    successful_inserts = []

    def inserter(start, count):
        local_success = 0
        for i in range(start, start + count):
            r = ht.Hash_Insert(i)
            if r == 0:
                local_success += 1
        with insert_lock:
            successful_inserts.append(local_success)

    threads = [threading.Thread(target=inserter, args=(t * 100, 100))
               for t in range(10)]
    for th in threads: th.start()
    for th in threads: th.join()

    expected = sum(successful_inserts)
    actual   = ht.Hash_CountElements()
    log(f"CountElements matches successful inserts ({expected})",
        actual == expected, f"got {actual}")


# ── Test 7: Stress Test ───────────────────────────────────────────────────────

def test_stress():
    header("Stress Test (high concurrency, random operations)")
    NUM_BUCKETS = 64
    NUM_THREADS = 50
    OPS_PER_THREAD = 200
    VALUE_RANGE = 500      # values 0–499; collisions expected

    ht = HashTable()
    ht.Hash_Init(NUM_BUCKETS)

    # Track net inserts with a thread-safe counter
    net_counter_lock = threading.Lock()
    net_elements = [0]   # use list so closure can mutate

    def worker():
        local_net = 0
        for _ in range(OPS_PER_THREAD):
            val = random.randint(0, VALUE_RANGE - 1)
            op  = random.choice(["insert", "remove"])
            if op == "insert":
                r = ht.Hash_Insert(val)
                if r == 0:
                    local_net += 1
            else:
                r = ht.Hash_Remove(val)
                if r == 0:
                    local_net -= 1
        with net_counter_lock:
            net_elements[0] += local_net

    threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
    start = time.time()
    for th in threads: th.start()
    for th in threads: th.join()
    elapsed = time.time() - start

    expected = net_elements[0]
    actual   = ht.Hash_CountElements()
    log(f"Stress: expected={expected}, actual={actual}",
        actual == expected, f"elapsed={elapsed:.2f}s")

    print(f"\n  Stress stats:")
    print(f"    Threads       : {NUM_THREADS}")
    print(f"    Ops per thread: {OPS_PER_THREAD}")
    print(f"    Total ops     : {NUM_THREADS * OPS_PER_THREAD:,}")
    print(f"    Elapsed time  : {elapsed:.3f}s")
    print(f"    Throughput    : {int(NUM_THREADS * OPS_PER_THREAD / elapsed):,} ops/sec")


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary():
    print(f"\n{'='*60}")
    print("  FINAL TEST RESULTS")
    print(f"{'='*60}")
    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        mark = PASS if ok else FAIL
        print(f"  {mark}  {name}")
    print(f"\n  {passed}/{len(results)} tests passed.")
    print(f"{'='*60}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("MIT102 Assessment 3 — Thread-Safe Hash Table Tests")
    print("=" * 60)

    test_basic()
    test_concurrent_inserts()
    test_concurrent_removes()
    test_mixed_concurrent()
    test_concurrent_duplicates()
    test_count_accuracy()
    test_stress()

    print_summary()
