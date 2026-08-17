"""
MIT102 - Operating Systems and Computer Architecture
Assessment 3: Thread-Safe Hash Table

Design:
  - One lock per bucket (fine-grained locking) — avoids contention
  - Each bucket holds a singly-linked list of integers
  - All public methods are thread-safe
  - Error handling: prints message and exits on unexpected failures
"""

import threading
import sys


# ── Linked List Node ──────────────────────────────────────────────────────────

class Node:
    """A single node in a bucket's linked list."""
    def __init__(self, value: int):
        self.value = value
        self.next = None


# ── Thread-Safe Hash Table ────────────────────────────────────────────────────

class HashTable:
    """
    Thread-safe hash table storing integers.

    Uses one mutex lock per bucket (fine-grained locking).
    Each bucket maintains a singly linked list of integers.

    Bucket selection: bucketNum = x % numOfBuckets
    """

    def __init__(self):
        self._buckets = None        # list of Node heads
        self._locks = None          # one threading.Lock per bucket
        self._num_buckets = 0
        self._initialized = False

    # ── Hash_Init ─────────────────────────────────────────────────────────────

    def Hash_Init(self, numOfBuckets: int):
        """
        Initialize the hash table with the specified number of buckets.
        Creates one lock per bucket (fine-grained locking).
        """
        if numOfBuckets <= 0:
            print("[ERROR] numOfBuckets must be a positive integer.", file=sys.stderr)
            sys.exit(1)

        self._num_buckets = numOfBuckets

        try:
            self._buckets = [None] * numOfBuckets          # head node per bucket
            self._locks   = [threading.Lock() for _ in range(numOfBuckets)]
        except MemoryError as e:
            print(f"[ERROR] Failed to allocate hash table: {e}", file=sys.stderr)
            sys.exit(1)

        self._initialized = True
        print(f"[Hash_Init] Initialized with {numOfBuckets} buckets "
              f"({numOfBuckets} individual locks).")

    # ── Hash_Insert ───────────────────────────────────────────────────────────

    def Hash_Insert(self, x: int) -> int:
        """
        Insert integer x into the hash table.
        Returns  0 if successfully inserted.
        Returns -1 if x already exists (no duplicate inserted).
        """
        self._check_init()
        bucket = x % self._num_buckets

        with self._locks[bucket]:
            # Walk the linked list to check for duplicates
            current = self._buckets[bucket]
            while current is not None:
                if current.value == x:
                    return -1           # duplicate
                current = current.next

            # Prepend new node (O(1))
            try:
                new_node = Node(x)
            except MemoryError as e:
                print(f"[ERROR] malloc failed during Hash_Insert: {e}", file=sys.stderr)
                sys.exit(1)

            new_node.next = self._buckets[bucket]
            self._buckets[bucket] = new_node
            return 0

    # ── Hash_Remove ───────────────────────────────────────────────────────────

    def Hash_Remove(self, x: int) -> int:
        """
        Remove integer x from the hash table.
        Returns  0 if successfully removed.
        Returns -1 if x does not exist.
        """
        self._check_init()
        bucket = x % self._num_buckets

        with self._locks[bucket]:
            prev = None
            current = self._buckets[bucket]

            while current is not None:
                if current.value == x:
                    if prev is None:
                        self._buckets[bucket] = current.next   # remove head
                    else:
                        prev.next = current.next               # unlink
                    return 0
                prev = current
                current = current.next

            return -1       # not found

    # ── Hash_CountElements ────────────────────────────────────────────────────

    def Hash_CountElements(self) -> int:
        """
        Count and return the total number of elements in the hash table.
        Acquires each bucket lock in sequence to get a consistent snapshot.
        """
        self._check_init()
        total = 0
        for bucket in range(self._num_buckets):
            with self._locks[bucket]:
                current = self._buckets[bucket]
                while current is not None:
                    total += 1
                    current = current.next
        return total

    # ── Hash_CountBucketElements ──────────────────────────────────────────────

    def Hash_CountBucketElements(self, bucketNumber: int) -> int:
        """
        Count and return the number of elements in the specified bucket.
        """
        self._check_init()
        if not (0 <= bucketNumber < self._num_buckets):
            print(f"[ERROR] bucketNumber {bucketNumber} out of range "
                  f"(0–{self._num_buckets - 1}).", file=sys.stderr)
            sys.exit(1)

        count = 0
        with self._locks[bucketNumber]:
            current = self._buckets[bucketNumber]
            while current is not None:
                count += 1
                current = current.next
        return count

    # ── Hash_Dump ─────────────────────────────────────────────────────────────

    def Hash_Dump(self):
        """
        Print the full content of the hash table, bucket by bucket.
        Acquires each bucket lock while printing that bucket.
        """
        self._check_init()
        print("\n" + "=" * 50)
        print(f"  HASH TABLE DUMP  ({self._num_buckets} buckets)")
        print("=" * 50)
        for bucket in range(self._num_buckets):
            with self._locks[bucket]:
                elements = []
                current = self._buckets[bucket]
                while current is not None:
                    elements.append(str(current.value))
                    current = current.next
            if elements:
                print(f"  Bucket[{bucket:3d}]: {' -> '.join(elements)} -> NULL")
            else:
                print(f"  Bucket[{bucket:3d}]: (empty)")
        print("=" * 50)
        print(f"  Total elements: {self.Hash_CountElements()}")
        print("=" * 50 + "\n")

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _check_init(self):
        if not self._initialized:
            print("[ERROR] Hash table not initialized. Call Hash_Init() first.",
                  file=sys.stderr)
            sys.exit(1)
