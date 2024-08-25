from typing import Callable, Any, Literal
import time
import re


class Benchmark:
	sets_per_test: int
	runs_per_set: int
	__functions: list[Callable[[], Any]]
	__cases: dict[str : Callable[[], None]]
	__times_ns: dict[str, list[int]] | None

	def __init__(self, sets_per_test: int = 100, runs_per_set: int = 100) -> None:
		# TODO DOCSTRING
		self.sets_per_test = int(sets_per_test)
		self.runs_per_set = int(runs_per_set)
		self.__functions = []
		self.__cases = {}
		self.__reset_times()

	def set_functions(self, functions: list[Callable[[], Any] | str]):
		# TODO DOCSTRING
		self.__reset_times()
		self.__functions = []
		for f in functions:
			self.add_function(f)

	def add_function(self, fun: Callable[[], Any] | str):
		# TODO DOCSTRING
		if isinstance(fun, str):
			code = fun
			fun = eval("lambda: " + code)
			fun.__name__ = code
			fun.__doc__ = code
		self.__functions.append(fun)

	def set_cases(self, cases: dict[str, Callable[[], None] | str]):
		# TODO DOCSTRING
		self.__reset_times()
		self.__cases = {}
		for name, setup in cases.items():
			self.add_case(name, setup)

	def add_case(self, case_name: str, case_setup: Callable[[], None] | str):
		# TODO DOCSTRING
		if case_name in self.__cases:
			raise KeyError(f"Case name “{case_name}” already in use.")
		if isinstance(case_setup, str):
			code = case_setup
			case_setup = lambda: eval(code)
		self.__cases[case_name] = case_setup

	def run(self) -> None:
		self.__ensure_case()
		self.__times_ns = {}
		for case, setup in self.__cases.items():
			times_ns = [0] * len(self.__functions)
			self.__times_ns[case] = times_ns
			setup()
			for _ in range(self.sets_per_test):
				for i, f in enumerate(self.__functions):
					t = time.time_ns()
					for _ in range(self.runs_per_set):
						f()
					t = time.time_ns() - t
					times_ns[i] += t

	def report(
		self,
		normalize_with: Literal["min", "max"] | int | None = None,
		use_doc_as_name: bool = False,
	) -> None:
		# TODO DOCSTRING
		self.__ensure_run()
		lines = []
		if self.__has_cases():
			lines.append([""] + list(self.__cases.keys()))
		if normalize_with is not None:
			data = self.__normalized_times(normalize_with)
			format = lambda x: f"{x:.3f}"
		else:
			data = self.__times_ns
			format = lambda x: str(x)
		for i, f in enumerate(self.__functions):
			line = [f.__doc__ if use_doc_as_name and f.__doc__ else f.__name__]
			for case in self.__cases:
				line.append(format(data[case][i]))
			lines.append(line)
		print(self.__prettify_table(lines))

	def report_html(
		self,
		normalize_with: Literal["min", "max"] | int | None = None,
		use_doc_as_name: bool = False,
	):
		# TODO DOCSTRING
		self.__ensure_run()
		lines = []
		n_total = self.sets_per_test * self.runs_per_set
		f_names = [
			self.__html_format(f.__doc__)
			if use_doc_as_name and f.__doc__
			else f"<code>{f.__name__}</code>"
			for f in self.__functions
		]
		if normalize_with:
			if isinstance(normalize_with, int):
				ratio_text = f_names[normalize_with]
			else:
				ratio_text = {"min": "fastest", "max": "slowest"}
			ratio_text = f"<br>(ratio with {ratio_text})"
		else:
			ratio_text = ""
		lines.append(
			[
				f"<th>Executing</th><th colspan=\"{len(self.__cases)}\">Execution in ms, for {n_total:,} executions{ratio_text}</th>"
			]
		)
		if self.__has_cases():
			lines.append(
				["<th></th>"]
				+ [f"<th>{self.__html_format(case)}</th>" for case in self.__cases]
			)
		if normalize_with is not None:
			normalized = self.__normalized_times(normalize_with)
		for i, f in enumerate(f_names):
			line = [f"<td>{f}</td>"]
			for case in self.__cases:
				value = f"{self.__times_ns[case][i]/1000:,.1f}"
				if normalize_with is not None:
					value += f"<br>({normalized[case][i]:.2f})"
				line.append(f"<td>{value}</td>")
			lines.append(line)
		table = "<table>"
		for line in lines:
			table += f"\n  <tr>\n    {"\n    ".join(items for items in line)}\n  </tr>"
		table += "\n</table>"
		print(table)

	def __ensure_run(self) -> None:
		if self.__times_ns is None:
			self.run()

	def __ensure_case(self) -> None:
		if not self.__cases:
			self.__cases = {"": lambda: None}

	def __reset_times(self) -> None:
		self.__times_ns = None

	def __has_cases(self) -> bool:
		if not self.__cases:
			return False
		if len(self.__cases) > 1:
			return True
		for case_name in self.__cases:
			if case_name:
				return True
		return False

	def __normalized_times(
		self, norm: Literal["min", "max"] | int
	) -> dict[str, list[float]]:
		if isinstance(norm, int):
			norm_fun = lambda x: x[norm]
		else:
			norm_fun = {"min": min, "max": max}[norm]
		data = {}
		for case, values in self.__times_ns.items():
			div = norm_fun(values)
			data[case] = [x / div for x in values]
		return data

	def __prettify_table(self, table: list[list[str]]) -> str:
		width = [0] * len(table[0])
		for line in table:
			for col, string in enumerate(line):
				width[col] = max(width[col], len(string))
		lines = []
		sep = "   "
		for line in table:
			items = []
			for i, x in enumerate(line):
				if i == 0:
					items.append(f"{x:{width[0]}}")
				else:
					items.append(f"{x:>{width[i]}}")
			lines.append(sep.join(items))
		return "\n".join(lines)

	@staticmethod
	def __html_format(s) -> str:
		# This is knowingly bad… But enough for now.
		s = re.sub(r"(?<!\\)`((\S.*?)?[^\s\\])`", lambda m: f"<code>{m[1]}</code>", s)
		s = re.sub(r"(?<!\\)\*\*((\S.*?)?[^\s\\])\*\*", lambda m: f"<b>{m[1]}</b>", s)
		s = re.sub(r"(?<!\\)\*((\S.*?)?[^\s\\])\*", lambda m: f"<em>{m[1]}</em>", s)
		return s


if __name__ == "__main__":

	import numpy as np

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
		x_2d_ = x_2d + .1
		x_1d = x[i_bool2D]
		x_1d_ = x_1d + .1

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

	swap_idx = np.array([2,3])
	swap_idx_ = np.array([3,2])
	def swap2_2D():
		"""Swap 2 indices in a `NpArray2D[float]`"""
		global x_2d, swap_idx, swap_idx_
		x_2d[swap_idx,:] = x_2d[swap_idx_,:]
		x_2d[:,swap_idx] = x_2d[:,swap_idx_]


	def numpize_1D():
		"""Convert a `list[int]` into a `Vector[int]`"""
		global x_2d, i_list
		np.array(i_list)

	def swap2_1D():
		"""Swap 2 indices in a `Vector[int]`"""
		global x_2d, i_np
		i_np[(5,3),] = i_np[(3,5),]

	bm = Benchmark(sets_per_test=1000, runs_per_set=1000)
	bm.set_functions([
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
	])
	bm.set_cases(dict((f"n = {k}", eval(f"lambda: setup_case({k})")) for k in [8,16,24]))
	print()
	bm.report_html(normalize_with=1, use_doc_as_name=True)
	print()
