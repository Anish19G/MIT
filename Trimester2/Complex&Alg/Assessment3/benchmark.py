"""
MIT202 Complexity and Algorithms — Assessment 3
Empirical Benchmarking Script

Measures wall-clock runtime of four sorting algorithms across:
  - Three input distributions: random, sorted, reverse-sorted
  - Eight input sizes:        100 to 10,000 elements
  - Five repetitions each:    averaged to reduce noise

Outputs:
  - benchmark_results.csv   — raw timing data
  - Console summary table

Author : [Your Name]
Student: [Your Student ID]
Unit   : MIT202 Complexity and Algorithms
"""

import time
import random
import csv
import statistics
from algorithms import merge_sort, quick_sort, heap_sort, insertion_sort

# ── Configuration ──────────────────────────────────────────────────────────
SIZES       = [100, 250, 500, 1000, 2000, 3000, 5000, 10000]
REPETITIONS = 5
DISTRIBUTIONS = ["random", "sorted", "reverse"]

ALGORITHMS = {
    "Merge Sort"     : merge_sort,
    "Quick Sort"     : quick_sort,
    "Heap Sort"      : heap_sort,
    "Insertion Sort" : insertion_sort,
}

# Insertion sort is very slow at large n — cap it
INSERTION_SORT_MAX = 3000


def generate_input(size, distribution):
    """Generate a list of `size` integers for the given distribution."""
    if distribution == "random":
        return [random.randint(0, 100_000) for _ in range(size)]
    elif distribution == "sorted":
        return list(range(size))
    elif distribution == "reverse":
        return list(range(size, 0, -1))
    else:
        raise ValueError(f"Unknown distribution: {distribution}")


def time_algorithm(func, arr):
    """Return wall-clock time in milliseconds to sort a copy of arr."""
    data = list(arr)        # ensure function works on a fresh copy
    start = time.perf_counter()
    func(data)
    end = time.perf_counter()
    return (end - start) * 1000   # ms


def run_benchmarks():
    """Run all benchmarks; return list of result dicts."""
    results = []
    total_runs = len(DISTRIBUTIONS) * len(SIZES) * len(ALGORITHMS)
    run = 0

    print(f"\n{'='*65}")
    print(f"  MIT202 — Sorting Algorithm Benchmark")
    print(f"  Sizes: {SIZES}")
    print(f"  Repetitions per test: {REPETITIONS}")
    print(f"{'='*65}\n")

    for dist in DISTRIBUTIONS:
        print(f"  Distribution: {dist.upper()}")
        print(f"  {'Algorithm':<18} {'n':>6}  {'Avg (ms)':>10}  {'Std (ms)':>10}")
        print(f"  {'-'*50}")

        for size in SIZES:
            # Generate base input once; reuse across algorithms
            base = generate_input(size, dist)

            for alg_name, alg_func in ALGORITHMS.items():
                run += 1

                # Skip large insertion sort (impractically slow)
                if alg_name == "Insertion Sort" and size > INSERTION_SORT_MAX:
                    results.append({
                        "algorithm"   : alg_name,
                        "distribution": dist,
                        "n"           : size,
                        "avg_ms"      : None,
                        "std_ms"      : None,
                        "skipped"     : True,
                    })
                    continue

                times = []
                for _ in range(REPETITIONS):
                    t = time_algorithm(alg_func, base)
                    times.append(t)

                avg = statistics.mean(times)
                std = statistics.stdev(times) if len(times) > 1 else 0.0

                results.append({
                    "algorithm"   : alg_name,
                    "distribution": dist,
                    "n"           : size,
                    "avg_ms"      : round(avg, 4),
                    "std_ms"      : round(std, 4),
                    "skipped"     : False,
                })

                print(f"  {alg_name:<18} {size:>6}  {avg:>10.4f}  {std:>10.4f}")

        print()

    return results


def save_csv(results, path="benchmark_results.csv"):
    """Save results to CSV for reproducibility."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["algorithm","distribution","n","avg_ms","std_ms","skipped"])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results saved to {path}\n")


def print_summary(results):
    """Print a summary table of averages per algorithm and distribution."""
    print(f"\n{'='*65}")
    print("  SUMMARY — Average runtime (ms) for n=10,000 (random input)")
    print(f"{'='*65}")
    for alg in ALGORITHMS:
        row = next((r for r in results
                    if r["algorithm"] == alg
                    and r["distribution"] == "random"
                    and r["n"] == 10000), None)
        if row and not row["skipped"]:
            print(f"  {alg:<20}: {row['avg_ms']:>10.4f} ms")
        else:
            print(f"  {alg:<20}: {'N/A (skipped)':>10}")
    print(f"{'='*65}\n")


def verify_correctness():
    """Quick sanity check that all algorithms produce correct output."""
    print("  Verifying correctness...")
    test = [random.randint(0, 1000) for _ in range(200)]
    expected = sorted(test)
    for name, func in ALGORITHMS.items():
        result = func(list(test))
        assert result == expected, f"{name} produced incorrect output!"
    print("  All algorithms verified correct.\n")


if __name__ == "__main__":
    random.seed(42)   # reproducibility
    verify_correctness()
    results = run_benchmarks()
    save_csv(results)
    print_summary(results)
