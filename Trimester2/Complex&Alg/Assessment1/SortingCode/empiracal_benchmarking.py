import argparse
import csv
import random
import time
import tracemalloc
import statistics
import math
import os

try:
	import matplotlib.pyplot as plt
	import numpy as np
except Exception:
	plt = None
	np = None


def insertion_sort(arr):
	a = arr
	for i in range(1, len(a)):
		key = a[i]
		j = i - 1
		while j >= 0 and a[j] > key:
			a[j + 1] = a[j]
			j -= 1
		a[j + 1] = key
	return a


def merge_sort(arr):
	if len(arr) <= 1:
		return arr
	mid = len(arr) // 2
	left = merge_sort(arr[:mid])
	right = merge_sort(arr[mid:])
	merged = []
	i = j = 0
	while i < len(left) and j < len(right):
		if left[i] <= right[j]:
			merged.append(left[i])
			i += 1
		else:
			merged.append(right[j])
			j += 1
	merged.extend(left[i:])
	merged.extend(right[j:])
	return merged


def measure_time_and_memory(func, data, repeat=1):
	# Measure time (average over repeat runs) and memory (single run peak)
	times = []
	mem_peak = None
	for _ in range(repeat):
		arr_copy = list(data)
		tracemalloc.start()
		t0 = time.perf_counter()
		# run
		res = func(arr_copy)
		t1 = time.perf_counter()
		current, peak = tracemalloc.get_traced_memory()
		tracemalloc.stop()
		times.append(t1 - t0)
		mem_peak = peak if mem_peak is None else max(mem_peak, peak)
	return statistics.mean(times), mem_peak


def run_benchmarks(sizes, out_csv='benchmark_results.csv', out_plot='benchmark_plot.png'):
	algos = [
		('Insertion Sort', insertion_sort),
		('Merge Sort', merge_sort),
	]

	rows = []

	# For insertion sort, extremely large inputs (like 50k) are infeasible in reasonable time.
	# We'll skip insertion for the largest size and record as skipped.
	for n in sizes:
		print(f"\nData size: {n}")
		base = [random.randint(0, n * 10) for _ in range(n)]
		row = {'n': n}
		for name, func in algos:
			# decide repeats
			if name == 'Insertion Sort' and n > 10000:
				print(f"- {name}: skipped for n={n} (impractical)" )
				row[f'{name}_time'] = None
				row[f'{name}_mem'] = None
				continue
			repeat = 3 if n <= 10000 else 1
			print(f"- Running {name} (repeat={repeat})...")
			t, mem = measure_time_and_memory(func, base, repeat=repeat)
			print(f"  time={t:.6f}s, mem_peak={mem} bytes")
			row[f'{name}_time'] = t
			row[f'{name}_mem'] = mem
		rows.append(row)

	# Write CSV
	fieldnames = ['n'] + [f'{a[0]}_time' for a in algos] + [f'{a[0]}_mem' for a in algos]
	with open(out_csv, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for r in rows:
			writer.writerow(r)
	print(f"\nResults saved to {out_csv}")

	# Plot runtime comparison
	if plt is None or np is None:
		print('matplotlib or numpy not available; skipping plot.')
		return rows

	ns = [r['n'] for r in rows]
	ins_times = [r['Insertion Sort_time'] if r['Insertion Sort_time'] is not None else float('nan') for r in rows]
	mrg_times = [r['Merge Sort_time'] for r in rows]

	plt.figure(figsize=(8, 5))
	plt.plot(ns, ins_times, marker='o', label='Insertion Sort')
	plt.plot(ns, mrg_times, marker='o', label='Merge Sort')
	plt.xlabel('N (input size)')
	plt.ylabel('Time (s)')
	plt.title('Insertion Sort vs Merge Sort — Runtime')
	plt.xscale('log')
	plt.yscale('log')
	plt.grid(True, which='both', ls='--', lw=0.5)
	plt.legend()
	plt.tight_layout()
	plt.savefig(out_plot)
	print(f"Plot saved to {out_plot}")
	return rows


def interpretation_text(rows):
	lines = []
	lines.append('Interpretation of empirical results:')
	lines.append('')
	lines.append('Theoretical expectations:')
	lines.append('- Insertion Sort: O(n^2) — time grows quadratically with n.')
	lines.append('- Merge Sort: O(n log n) — time grows roughly like n log n.')
	lines.append('')
	lines.append('Observed behaviour:')
	for r in rows:
		n = r['n']
		ins = r.get('Insertion Sort_time')
		mrg = r.get('Merge Sort_time')
		if ins is None:
			lines.append(f'- n={n}: Insertion Sort skipped (impractical), Merge Sort time {mrg:.6f}s')
		else:
			lines.append(f'- n={n}: Insertion {ins:.6f}s, Merge {mrg:.6f}s')
	lines.append('')
	lines.append('Conclusion:')
	lines.append('Merge Sort scales far better than Insertion Sort for larger n; the empirical results match theoretical expectations. Any deviations (small constant-factor differences) are likely due to Python interpreter overhead, memory allocation, and the particular random data distributions used.')
	return '\n'.join(lines)


def main():
	parser = argparse.ArgumentParser(description='Empirical benchmarking of sorting algorithms')
	parser.add_argument('--quick', action='store_true', help='Run a quick test with small sizes')
	parser.add_argument('--out-csv', default='benchmark_results.csv')
	parser.add_argument('--out-plot', default='benchmark_plot.png')
	args = parser.parse_args()

	if args.quick:
		sizes = [100, 500, 1000, 2000]
	else:
		sizes = [1000, 5000, 10000, 50000]

	rows = run_benchmarks(sizes, out_csv=args.out_csv, out_plot=args.out_plot)
	text = interpretation_text(rows)
	with open('interpretation.txt', 'w', encoding='utf-8') as f:
		f.write(text)
	print('\n' + text)


if __name__ == '__main__':
	main()

