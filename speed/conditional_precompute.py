import numpy as np
from numpy.typing import NDArray
from benchmark import Benchmark

n_total = 26
freq_matrix = np.random.rand(n_total, n_total)
false = False

cost_matrix: NDArray
fixed_idx: list[int]
perm_idx = tuple[int]


def setup(n: int):
	global cost_matrix, fixed_idx, perm_idx
	cost_matrix = np.random.rand(n, n)
	fixed_idx = list(range(n - 8))
	perm_idx = tuple(range(n - 8, n))


def score():
	idx = fixed_idx + list(perm_idx)
	return np.sum(cost_matrix * freq_matrix[idx, :][:, idx])


def score_with_if():
	if false:
		precompute()
	idx = fixed_idx + list(perm_idx)
	return np.sum(cost_matrix * freq_matrix[idx, :][:, idx])


def score_with_if_subs():
	precompute_if_needed()
	return score()


def precompute_if_needed():
	if false:
		precompute()


def precompute():
	return None


if __name__ == "__main__":
	bm = Benchmark(sets_per_test=1000)
	bm.set_cases(dict((f"n = {n}", eval(f"lambda: setup({n})")) for n in [8, 16, 24]))
	bm.set_functions([score, score_with_if, score_with_if_subs])
	bm.report()
