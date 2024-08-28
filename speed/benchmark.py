from typing import Callable, Any, Literal
import time
import re
import warnings # hack

class Benchmark:
	sets_per_test: int
	runs_per_set: int
	setup_once: bool
	__functions: list[Callable[[], Any]]
	__cases: dict[str : Callable[[], None]]
	__times_ns: dict[str, list[int]] | None

	def __init__(self, sets_per_test: int = 100, runs_per_set: int = 100) -> None:
		"""
		Create a Benchmark object that would run each one of the tested functions or commands
		`runs_per_set` times (default: `100`), `sets_per_test` times (default: `100`).
		"""
		self.sets_per_test = int(sets_per_test)
		self.runs_per_set = int(runs_per_set)
		self.setup_once = True
		self.__functions = []
		self.__cases = {}
		self.__reset_times()

	def set_functions(self, functions: list[Callable[[], Any] | str]):
		"""
		Set the list of functions to be run and timed by the Benchmark object.
		Those functions must take no argument.
		Alternatively, strings can be provided in lieu of functions, in which case
		what is measured is the time to execute the evaluated string.
		"""
		self.__reset_times()
		self.__functions = []
		for f in functions:
			self.add_function(f)

	def add_function(self, fun: Callable[[], Any] | str):
		"""
		Add a function to the list of functions to be run and timed by the Benchmark object.
		This functions must take no argument.
		Alternatively, a string can be provided instead of a function, in which case
		what is measured is the time to execute the evaluated string.
		"""
		if isinstance(fun, str):
			code = fun
			fun = eval("lambda: " + code)
			fun.__name__ = code
			fun.__doc__ = code
		self.__functions.append(fun)

	def set_cases(self, cases: dict[str, Callable[[], None] | str]):
		"""
		Set cases for which the target functions or commands must be timed.
		Each case is defined by a name (its key in the dictionary provided as argument),
		and a setup function taking no argument (the attached value).
		This setup function is typically used to setup global variables that are used
		in the target functions or commands.\n
		By default, the setup function is run only once before running all functions many times.
		In order to run it every time before running a test function, set the attribute
		`.setup_once` to `False`.
		"""
		self.__reset_times()
		self.__cases = {}
		for name, setup in cases.items():
			self.add_case(name, setup)

	def add_case(self, case_name: str, case_setup: Callable[[], None] | str):
		"""
		Add a case for which the target functions or commands must be timed.
		The case is defined by a name (`case_name`),
		and a setup function taking no argument (`case_setup`).
		This setup function is typically used to setup global variables that are used
		in the target functions or commands.\n
		By default, the setup function is run only once before running all functions many times.
		In order to run it every time before running a test function, set the attribute
		`.setup_once` to `False`.
		"""
		if case_name in self.__cases:
			raise KeyError(f"Case name “{case_name}” already in use.")
		if isinstance(case_setup, str):
			code = case_setup
			case_setup = lambda: eval(code)
		self.__cases[case_name] = case_setup

	def run(self) -> None:
		"""
		Run and time the target functions and/or commands, for each target case (if relevant).
		"""
		self.__init_run()
		for case, setup in self.__cases.items():
			times_ns = [0] * len(self.__functions)
			self.__times_ns[case] = times_ns
			if self.setup_once:
				setup()
				self.__run_functions_without_setup(times_ns)
			else:
				self.__run_functions_with_setup(times_ns, setup)
			for _ in range(self.sets_per_test):
				for i, f in enumerate(self.__functions):
					t = time.time_ns()
					for _ in range(self.runs_per_set):
						f()
					t = time.time_ns() - t
					times_ns[i] += t
	
	def __init_run(self) -> None:
		self.__ensure_case()
		self.__times_ns = {}
		self.warned = False  # hack
	
	def __run_functions_without_setup(self, times_ns: list[int]) -> None:
		for _ in range(self.sets_per_test):
			for i, f in enumerate(self.__functions):
				t = time.time_ns()
				for _ in range(self.runs_per_set):
					f()
				t = time.time_ns() - t
				times_ns[i] += t

	def __run_functions_with_setup(self, times_ns: list[int], setup: Callable[[], None]) -> None:
		if not self.warned:  # hack
			warnings.warn("Case setup times are included in the results.")  # hack
			self.warned = True  # hack
		for _ in range(self.sets_per_test):
			for i, f in enumerate(self.__functions):
				t = time.time_ns()
				for _ in range(self.runs_per_set):
					setup()
					f()
				t = time.time_ns() - t
				times_ns[i] += t
	
	def report(
		self,
		normalize_with: Literal["min", "max"] | int | None = None,
		use_doc_as_name: bool = False,
	) -> None:
		"""
		Report the run times in the terminal.
		- `normalize_with`: If not `None`, the results are normalized by dividing them by:
			- The time for the *n*-th function/command `normalize_with` is an integer *n*.
			- The smallest time (on a case-by-case basis) if `normalize_with = "min"`.
			- The largest time (on a case-by-case basis) if `normalize_with = "max"`.
		- `use_doc_as_name`: Use the docstring of the function (if any) to designate it.
		"""
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
		"""
		Report the run times as an html table.
		- `normalize_with`: If not `None`, the results are normalized by dividing them by:
			- The time for the *n*-th function/command `normalize_with` is an integer *n*.
			- The smallest time (on a case-by-case basis) if `normalize_with = "min"`.
			- The largest time (on a case-by-case basis) if `normalize_with = "max"`.
		- `use_doc_as_name`: Use the docstring of the function (if any) to designate it.
		"""
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


