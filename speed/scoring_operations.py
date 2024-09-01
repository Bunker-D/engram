import numpy as np
from benchmark import Benchmark

n = 26
x = np.random.rand(n, n)

i_sl = None
i_list = None
i_tuple = None
i_np = None
i_bool = None
i_bool_np = None
i_bool2D = None


def setup_case(k):
	global sub_n, i_sl, i_list, i_tuple, i_np, i_bool, i_bool_np, i_bool2D, x_2d, x_2d_, x_1d, x_1d_
	sub_n = k
	i_sl = slice(k)
	i_list = list(range(k))
	i_tuple = tuple(i_list)
	i_np = np.array(i_list)
	i_bool = [True] * k + [False] * (n - k)
	i_bool_np = np.array(i_bool)
	i_bool2D = np.full(x.shape, False)
	i_bool2D[i_sl, i_sl] = True
	x_2d = x[i_sl, :][:, i_sl]
	x_2d_ = x_2d + 0.1
	x_1d = x[i_bool2D]
	x_1d_ = x_1d + 0.1


def sel_sl_raw():
	"""`m[:n, :][:, :n]` with `n: int`"""
	global x, sub_n
	x[:sub_n, :][:, :sub_n]


def sel_sl():
	"""`m[i, :][:, i]` with `i: slice`"""
	global x, i_sl
	x[i_sl, :][:, i_sl]


def sel_list():
	"""`m[i, :][:, i]` with `i: list[int]`"""
	global x, i_list
	x[i_list, :][:, i_list]


def sel_tuple():
	"""`m[i, :][:, i]` with `i: tuple[int]`"""
	global x, i_tuple
	x[i_tuple, :][:, i_tuple]


def sel_np():
	"""`m[i, :][:, i]` with `i: NpVector[int]`"""
	global x, i_np
	x[i_np, :][:, i_np]


def sel_np_list():
	"""with `i: tuple[int]` converted to `NpVector[int]`"""
	global x, i_tuple
	i = np.array(i_tuple)
	x[i, :][:, i]


def sel_bool():
	"""`m[i, :][:, i]` with `i: list[bool]`"""
	global x, i_bool
	x[i_bool, :][:, i_bool]


def sel_bool_np():
	"""`m[i, :][:, i]` with `i: NpVector[bool]`"""
	global x, i_bool_np
	x[i_bool_np, :][:, i_bool_np]


def sel_bool2D():
	"""`m[i]` with `i: NpArray2D[bool]`"""
	global x, i_bool2D
	x[i_bool2D]


def prod_2d():
	"""`m * M` with `m,M: NpArray2D[float]`"""
	global x_2d, x_2d_
	x_2d * x_2d_


def prod_1d():
	"""`m * M` with `m,M: NpVector[float]`"""
	global x_1d, x_1d_
	x_1d * x_1d_


def sum_2d():
	"""`np.sum(m)` with `m: NpArray2D[float]`"""
	global x_2d
	np.sum(x_2d)


def sum_1d():
	"""`np.sum(m)` with `m: NpVector[float]`"""
	global x_1d
	np.sum(x_1d)


def flatten():
	"""`np.flatten(m)` with `m: NpArray2D[float]`"""
	global x_2d
	x_2d.flatten()


def sum_prod():
	"""`np.sum( m * M )` with `m,M: NpArray2D[float]`"""
	global x_2d, x_2d_
	np.sum(x_2d * x_2d_)


def sum_prod_flattened():
	"""`np.sum( m.flatten() * M.flatten() )`"""
	global x_2d, x_2d_
	np.sum(x_2d.flatten() * x_2d_.flatten())


swap_idx = np.array([2, 3])
swap_idx_ = np.array([3, 2])


def swap2_2D():
	"""Swap 2 indices in a `NpArray2D[float]`"""
	global x_2d, swap_idx, swap_idx_
	x_2d[swap_idx, :] = x_2d[swap_idx_, :]
	x_2d[:, swap_idx] = x_2d[:, swap_idx_]


def numpize_1D():
	"""Convert a `list[int]` into a `Vector[int]`"""
	global x_2d, i_list
	np.array(i_list)


def swap2_1D():
	"""Swap 2 indices in a `Vector[int]`"""
	global x_2d, i_np
	i_np[(5, 3),] = i_np[
		(3, 5),
	]


if __name__ == "__main__":

	bm = Benchmark(sets_per_test=1000, runs_per_set=1000)
	bm.set_functions(
		[
			sel_sl_raw,
			sel_sl,
			sel_list,
			sel_tuple,
			sel_np,
			sel_np_list,
			sel_bool,
			sel_bool_np,
			sel_bool2D,
			prod_1d,
			prod_2d,
			sum_1d,
			sum_2d,
			flatten,
			sum_prod,
			sum_prod_flattened,
			swap2_2D,
			numpize_1D,
			swap2_1D,
		]
	)
	bm.set_cases(
		dict((f"n = {k}", eval(f"lambda: setup_case({k})")) for k in [8, 16, 24])
	)
	print()
	# bm.report(use_doc_as_name=True)
	bm.report_html(normalize_with=1, use_doc_as_name=True)
	print()
