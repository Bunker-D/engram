import numpy as np
from numpy.typing import NDArray
from itertools import permutations
from benchmark import Benchmark

n = 4 * 8  # 26
costs = np.random.rand(n, n)
freqs = np.random.rand(n, n)

n_fixed: int
n_opened: int

keys_f: list[int]
chars_f: list[int]
keys_o: list[int]
chars_o: list[int]

costs_ff: NDArray = np.array([])
freqs_ff: NDArray = np.array([])
costs_oo: NDArray = np.array([])
freqs_oo: NDArray = np.array([])
costs_fo: NDArray = np.array([])
freqs_fo: NDArray = np.array([])
costs_of: NDArray = np.array([])
freqs_of: NDArray = np.array([])

sample_chars_new: tuple[int, ...]
sample_chars_raw: tuple[int, ...]


def setup(n_fixed_: int, n_opened_: int):
	global n_fixed, n_opened
	global keys_f, chars_f, keys_o, chars_o
	global costs_reduced  # , costs_f, costs_o
	global costs_ff, freqs_ff, costs_oo, freqs_oo
	global costs_fo, freqs_fo, costs_of, freqs_of
	global score_ff, score_fo_of
	global sample_chars_new, sample_chars_raw
	global range_opened
	n_fixed = n_fixed_
	n_opened = n_opened_
	keys_f = list(range(n_fixed))
	chars_f = list(range(n_fixed))
	keys_o = list(n_fixed + i for i in range(n_opened))
	chars_o = list(n_fixed + i for i in range(n_opened))
	# For naive, full multiplication
	keys_r = keys_f + keys_o
	costs_reduced = costs[keys_r, :][:, keys_r]
	# For pre-split calculation
	score_ff = np.sum(costs[keys_f, :][:, keys_f] * freqs[chars_f, :][:, chars_f])
	costs_fo = costs[keys_f, :][:, keys_o]
	freqs_fo = freqs[chars_f, :][:, chars_o]
	costs_of = costs[keys_o, :][:, keys_f]
	freqs_of = freqs[chars_o, :][:, chars_f]
	costs_oo = costs[keys_o, :][:, keys_o]
	freqs_oo = freqs[chars_o, :][:, chars_o]
	score_fo_of = pre_fo_of_3d()
	#
	sample_chars_new = tuple(np.argsort(np.random.rand(n_opened)))
	sample_chars_raw = tuple(chars_o[i] for i in sample_chars_new)
	range_opened = tuple(range(n_opened))


# Computing the fo_fo component of the score


def pre_fo_of_loop():
	"""… using a loop"""
	global n_opened
	global costs_fo, freqs_fo, costs_of, freqs_of
	score_fo_of = np.empty((n_opened, n_opened))
	for i in range(n_opened):
		score_fo_of[:, i] = np.sum(costs_fo * freqs_fo[:, (i,)], axis=0) + np.sum(
			costs_of * freqs_of[(i,), :], axis=1
		)
	return score_fo_of


def pre_fo_of_3d():
	"""… using 3D matrices"""
	global costs_fo, freqs_fo, costs_of, freqs_of
	costs_fo_3d = costs_fo[:, :, np.newaxis]
	freqs_fo_3d = freqs_fo[:, :, np.newaxis].transpose((0, 2, 1))
	score_fo = np.sum(costs_fo_3d * freqs_fo_3d, axis=0)
	costs_of_3d = costs_of[:, :, np.newaxis]
	freqs_of_3d = freqs_of[:, :, np.newaxis].transpose((2, 1, 0))
	score_of = np.sum(costs_of_3d * freqs_of_3d, axis=1)
	return score_fo + score_of


def assert_valid_fo_of():
	score_fo_of = pre_fo_of_loop()
	score_fo_of_ = pre_fo_of_3d()
	# Assert same results
	assert np.all(score_fo_of == score_fo_of_)
	# Assert valid results
	for i in range(n_opened):
		for j in range(n_opened):
			x = np.sum(costs_fo[:, i] * freqs_fo[:, j]) + np.sum(
				costs_of[i, :] * freqs_of[j, :]
			)
			assert score_fo_of[i, j] == x


# Computing the score


def score_direct(chars_raw: tuple[int, ...]):
	chars = chars_f + list(chars_raw)
	return np.sum(costs_reduced * freqs[chars, :][:, chars])


def score_split(chars_new: tuple[int, ...]):
	return (
		score_ff
		# + np.sum(score_fo_of[range(n_opened), chars_new])
		+ np.sum(score_fo_of[range_opened, chars_new])
		+ np.sum(costs_oo * freqs_oo[chars_new, :][:, chars_new])
	)


def assert_valid_score():
	global chars_o
	for chars_new in permutations(range(n_opened)):
		chars_raw = tuple(chars_o[i] for i in chars_new)
		assert np.isclose(score_direct(chars_raw), score_split(chars_new))


def score_direct_once():
	score_direct(sample_chars_raw)


def score_split_once():
	score_split(sample_chars_new)


def score_direct_all():
	for chars in permutations(chars_o):
		score_direct(chars)


def score_split_all():
	for chars in permutations(range(n_opened)):
		score_split(chars)


if __name__ == "__main__":
	setup(5, 3)
	print()
	assert_valid_fo_of()
	assert_valid_score()

	cases = dict((f"f {k}, o 8", eval(f"lambda: setup({k},8)")) for k in [0, 8, 16, 24])

	bm = Benchmark(sets_per_test=100, runs_per_set=100)
	bm.set_cases(cases)
	bm.set_functions([pre_fo_of_loop, pre_fo_of_3d])
	print()
	bm.report()

	bm.set_functions([score_direct_once, score_split_once])
	print()
	bm.report()

	bm = Benchmark(sets_per_test=1, runs_per_set=1)
	bm.set_cases(cases)
	bm.set_functions([score_direct_all, score_split_all])
	print()
	bm.report()
