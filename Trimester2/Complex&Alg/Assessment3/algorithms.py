"""
MIT202 Complexity and Algorithms — Assessment 3
Algorithm Implementation & Empirical Benchmarking

Problem: Sorting large datasets efficiently
Algorithms compared:
  1. Merge Sort     — O(n log n) divide and conquer
  2. Quick Sort     — O(n log n) average, O(n^2) worst case
  3. Heap Sort      — O(n log n) in-place
  4. Insertion Sort — O(n^2) baseline comparison

Author : [Your Name]
Student: [Your Student ID]
Unit   : MIT202 Complexity and Algorithms
"""

import time
import random
import sys
import csv
import copy

# ── Increase recursion limit for large inputs ──────────────────────────────
sys.setrecursionlimit(50000)


# ═══════════════════════════════════════════════════════════════════════════
# 1. MERGE SORT  — O(n log n) time, O(n) space
# ═══════════════════════════════════════════════════════════════════════════

def merge_sort(arr):
    """
    Divide-and-conquer sort.
    Recursively splits the array into halves, sorts each half,
    then merges the two sorted halves in O(n) time.

    Time  : O(n log n) — best, average, worst
    Space : O(n)       — auxiliary array during merge
    Stable: Yes
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    """Merge two sorted arrays into one sorted array."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ═══════════════════════════════════════════════════════════════════════════
# 2. QUICK SORT  — O(n log n) average, O(n^2) worst
# ═══════════════════════════════════════════════════════════════════════════

def quick_sort(arr):
    """
    Wrapper — copies array so in-place sort doesn't mutate caller's data.
    """
    arr = list(arr)
    _quick_sort(arr, 0, len(arr) - 1)
    return arr


def _quick_sort(arr, low, high):
    """
    Lomuto partition scheme with median-of-three pivot selection
    to reduce worst-case probability on sorted/nearly-sorted inputs.

    Time  : O(n log n) average, O(n^2) worst
    Space : O(log n)   stack frames (average)
    Stable: No
    """
    if low < high:
        pivot_idx = _partition(arr, low, high)
        _quick_sort(arr, low, pivot_idx - 1)
        _quick_sort(arr, pivot_idx + 1, high)


def _median_of_three(arr, low, high):
    """Return index of median of arr[low], arr[mid], arr[high]."""
    mid = (low + high) // 2
    a, b, c = arr[low], arr[mid], arr[high]
    if (a <= b <= c) or (c <= b <= a):
        return mid
    elif (b <= a <= c) or (c <= a <= b):
        return low
    else:
        return high


def _partition(arr, low, high):
    """Lomuto partition with median-of-three pivot."""
    pivot_idx = _median_of_three(arr, low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# ═══════════════════════════════════════════════════════════════════════════
# 3. HEAP SORT  — O(n log n) time, O(1) space
# ═══════════════════════════════════════════════════════════════════════════

def heap_sort(arr):
    """
    Builds a max-heap from the array, then repeatedly extracts
    the maximum element to produce a sorted output.

    Time  : O(n log n) — best, average, worst
    Space : O(1)       — in-place (excluding output copy here)
    Stable: No
    """
    arr = list(arr)
    n = len(arr)

    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)

    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]   # move current root to end
        _heapify(arr, i, 0)                # restore heap property

    return arr


def _heapify(arr, n, i):
    """Maintain the max-heap property rooted at index i."""
    largest = i
    left    = 2 * i + 1
    right   = 2 * i + 2

    if left  < n and arr[left]  > arr[largest]: largest = left
    if right < n and arr[right] > arr[largest]: largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify(arr, n, largest)


# ═══════════════════════════════════════════════════════════════════════════
# 4. INSERTION SORT  — O(n^2) — baseline / small-n comparison
# ═══════════════════════════════════════════════════════════════════════════

def insertion_sort(arr):
    """
    Simple comparison-based sort: builds sorted output one element at a time.
    Efficient for very small arrays (n < 20); used as baseline here.

    Time  : O(n^2) worst/average, O(n) best (already sorted)
    Space : O(1)
    Stable: Yes
    """
    arr = list(arr)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
