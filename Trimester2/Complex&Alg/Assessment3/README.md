# MIT202 — Complexity and Algorithms
**Assessment 3: Research-Informed Algorithm Study (Major Project)**  
Unit: MIT202 Complexity and Algorithms  
Worth: 40% of total unit marks  
Language: Python 3

---

## Overview

This project investigates four canonical comparison-based sorting algorithms through theoretical complexity analysis and empirical benchmarking. Algorithms are compared across varying input sizes and distributions to validate theoretical predictions and identify practical performance differences.

**Algorithms studied:**
- Merge Sort — O(n log n) guaranteed, stable, O(n) space
- Quick Sort — O(n log n) average with median-of-three pivot, O(log n) space
- Heap Sort — O(n log n) guaranteed, in-place, O(1) space
- Insertion Sort — O(n²) baseline, O(n) best case on sorted input

---

## Files

| File | Description |
|---|---|
| `algorithms.py` | All four sorting algorithm implementations with docstrings and pseudocode comments |
| `benchmark.py` | Empirical benchmarking suite — measures runtime across sizes and distributions |
| `benchmark_results.csv` | Raw timing output from the benchmark run (reproducible with seed 42) |
| `MIT202_Assessment3_Report.docx` | Full 10-section research report (~1,900 words) |
| `README.md` | This file |

---

## Requirements

- Python 3.6 or higher
- No external libraries required for `algorithms.py` or `benchmark.py`
- Standard library only: `time`, `random`, `csv`, `statistics`, `sys`

---

## How to Run

### 1. Verify algorithm correctness

```
python benchmark.py
```

The script automatically verifies all four algorithms against Python's built-in `sorted()` before running benchmarks. You will see:

```
Verifying correctness...
All algorithms verified correct.
```

### 2. Run the full benchmark

```
python benchmark.py
```

This runs all experiments and prints a live results table. On completion it saves `benchmark_results.csv` and prints a summary.

**Expected runtime:** approximately 3–5 minutes (due to Insertion Sort at large n).

### 3. Use algorithms independently

```python
from algorithms import merge_sort, quick_sort, heap_sort, insertion_sort

data = [5, 2, 8, 1, 9, 3]

print(merge_sort(data))      # [1, 2, 3, 5, 8, 9]
print(quick_sort(data))      # [1, 2, 3, 5, 8, 9]
print(heap_sort(data))       # [1, 2, 3, 5, 8, 9]
print(insertion_sort(data))  # [1, 2, 3, 5, 8, 9]
```

All functions return a new sorted list and do not modify the input.

---

## Benchmark Configuration

| Parameter | Value |
|---|---|
| Input sizes | 100, 250, 500, 1,000, 2,000, 3,000, 5,000, 10,000 |
| Input distributions | Random uniform, Ascending sorted, Reverse-sorted |
| Repetitions | 5 per (algorithm × size × distribution) |
| Metric | Average wall-clock time in milliseconds (ms) |
| Random seed | 42 (reproducible) |
| Insertion Sort cap | Skipped for n > 3,000 (too slow for meaningful comparison) |

---

## Example Output (n = 10,000, random input)

```
  Algorithm           Avg (ms)
  Merge Sort          17.3058
  Quick Sort          10.5754
  Heap Sort           22.5454
  Insertion Sort      N/A (skipped)
```

---

## Complexity Summary

| Algorithm | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |

---

## Key Findings

- **Quick Sort** is fastest on random input (10.58 ms at n=10,000) due to cache-friendly access patterns
- **Merge Sort** is most consistent across all distributions — recommended when input ordering is unpredictable
- **Heap Sort** is slowest despite O(1) space — poor cache locality increases constant factors significantly
- **Insertion Sort** is only competitive for small n or nearly-sorted data; 51–74x slower than Quick Sort at n=3,000

---

## Report Structure

The Word report (`MIT202_Assessment3_Report.docx`) follows the required structure:

1. Introduction
2. Literature Review — 6 IEEE/ACM sources critically synthesised
3. Problem Definition — formal problem statement and input distributions
4. Algorithm Design — pseudocode and justification for all 4 algorithms
5. Theoretical Analysis — recurrence relations, Master Theorem derivations
6. Experimental Methodology — benchmarking design and parameters
7. Results — 3 tables of empirical timing data
8. Discussion — theory vs practice, cache effects, distribution sensitivity
9. Conclusion — ranked recommendations for algorithm selection
10. References — Knuth, Hoare, Cormen, Sedgewick, Auger et al., Wild & Nebel

---

## Submission Checklist

- [ ] Fill in [Your Name] and [Student ID] in the report cover page and footer
- [ ] Run benchmark.py to regenerate your own benchmark_results.csv
- [ ] Convert MIT202_Assessment3_Report.docx to PDF for Moodle submission
- [ ] Submit both the PDF report and the .py files as required
