from typing import Literal

# > Building key data from descriptions in YAML


class Key:
    hand: Literal["L", "R"]
    finger: Literal[0, 1, 2, 3, 4]
    dx: int  # horizontal distance from rest position, > 0 ⇔ inward
    dy: int  # vertical   distance from rest position, > 0 ⇔ upward

    def __init__(self, finger: str, dx: int, dy: int) -> None:
        finger = finger.upper()
        self.__assert_valid_finger(finger)
        hand, finger, *_ = finger
        self.hand = hand  # type: ignore
        self.finger = "T1234".index(finger)  # type: ignore
        self.dx = dx
        self.dy = dy

    @staticmethod
    def __assert_valid_finger(finger: str) -> None:
        finger = finger.upper()
        if len(finger) < 2 or finger[0] not in "LR" or finger[1] not in "T1234":
            raise ValueError(f"Invalid finger: {finger}")

    def __str__(self) -> str:
        return f"{self.hand}{self.finger or 'T'}{self.movement()}"

    def movement(self) -> str:
        movement = ""
        y = self.dy
        x = self.dx
        if self.hand == "R":
            x *= -1
        while y or x:
            x_sign = self.__sign(x)
            y_sign = self.__sign(y)
            movement += {
                (-1,+1): "↖", (0,+1): "↑", (+1,+1): "↗",
                (-1, 0): "←",              (+1, 0): "→",
                (-1,-1): "↙", (0,-1): "↓", (+1,-1): "↘",
            }[x_sign, y_sign]  # fmt: skip
            x -= x_sign
            y -= y_sign
        return movement or "●"

    @staticmethod
    def __sign(x: int) -> Literal[-1, 0, 1]:
        if x < 0:
            return -1
        if x > 0:
            return 1
        return 0


# ruff:noqa: E501  #HACK

# class KeyboardDescr(TypedDict):
#     fingers: str
#     engram_id: str


# def main_keys(kb_descr: KeyboardDescr) -> list[Key]:
#     kb_keys: list[Key] = []
#     ids = (
#         i for l in kb_descr["engram_id"].strip().splitlines() for i in l.strip().split()
#     )
#     fingers_descr = kb_descr["fingers"].strip().splitlines()
#     home_row = next(i for i, l in enumerate(fingers_descr) if "*" in l)
#     for row, fingers_line in enumerate(fingers_descr):
#         per_finger: dict[str, list[Key]] = {"L4": [], "L1": [], "R1": [], "R4": []}
#         for finger in fingers_line.strip().split():
#             id = next(ids)
#             if id == "-":
#                 continue
#             finger = finger[:2]
#             key = Key(hand=finger[0], finger="T1234".index(finger[1]), v_dist=home_row - row, h_dist=0, engram_id=int(id))  # type: ignore
#             if finger not in per_finger:
#                 per_finger[finger] = []
#             per_finger[finger].append(key)
#             kb_keys.append(key)
#         per_finger["L4"].reverse()
#         per_finger["R1"].reverse()
#         for hand in "LR":
#             for i, key in enumerate(per_finger[f"{hand}4"]):
#                 key.h_dist = -i
#             for i, key in enumerate(per_finger[f"{hand}1"]):
#                 key.h_dist = i
#     kb_keys.sort(key=lambda k: k.engram_id)
#     return kb_keys


# with open("~kb.yml", "r", encoding="utf-8") as file:
#     kb_descr = KeyboardDescr(yaml.safe_load(file)["ANSI"])

# keys = main_keys(kb_descr)

# # > Comparison with original scoring


# original_scoring = __import__("~score_code")
# flow_matrix: Callable[..., NDArray] = original_scoring.create_32x32_flow_matrix
# flow_args = flow_matrix.__code__.co_varnames[: flow_matrix.__code__.co_argcount]

# # type Penalty = Callable[[Key,Key],float]
# type KeyPenaltyCondition = Callable[[Key], bool]
# type PairPenaltyCondition = Callable[[Key, Key], bool]


# no_penalties: list[str] = ["adjacent_offset"]

# # ▼ Condition tested for each key of the bigram. Penalty applied twice if condition applies twice.
# key_penalties: dict[str, KeyPenaltyCondition] = {
#     "lateral": lambda k: k.h_dist != 0,
#     "not_home_row": lambda k: k.v_dist != 0,
#     "side_top": lambda k: k.v_dist > 0 and k.finger in [1, 4],
#     "inside_top": lambda k: k.finger == 1 and k.v_dist > 0,
# }

# # ▼ Condition tested for the bigram.
# pair_penalties: dict[str, PairPenaltyCondition] = {  # Same hand is assumed!
#     "outward": lambda k0, k1: k0.hand == k1.hand and k1.finger > k0.finger,
#     "same_hand": lambda k0, k1: k0.hand == k1.hand,
#     "skip_row_0away": lambda k0, k1: (
#         k0.hand == k1.hand and k0.finger == k1.finger and abs(k0.v_dist - k1.v_dist) > 1
#     ),
#     "skip_row_1away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and abs(k0.finger - k1.finger) == 1
#         and abs(k0.v_dist - k1.v_dist) > 1
#     ),
#     "skip_row_2away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and abs(k0.finger - k1.finger) == 2
#         and abs(k0.v_dist - k1.v_dist) > 1
#     ),
#     "skip_row_3away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and abs(k0.finger - k1.finger) == 3
#         and abs(k0.v_dist - k1.v_dist) > 1
#     ),
#     "same_finger": lambda k0, k1: (
#         k0.hand == k1.hand and k0.finger == k1.finger and k0 != k1
#     ),
# }

# # ▼ Condition tested for the bigram and its reversion. Penalty applied twice if condition applies twice.
# sym_pair_penalties: dict[str, PairPenaltyCondition] = {
#     # ▲ Will be swapped too. Same hand is assumed!
#     "side_above_1away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and (k0.finger, k1.finger) in ((1, 2), (4, 3))
#         # ▲ ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 1
#         and k0.v_dist > k1.v_dist
#     ),
#     "side_above_2away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and (k0.finger, k1.finger) in ((1, 3), (4, 2))
#         # ▲ ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 2
#         and k0.v_dist > k1.v_dist
#     ),
#     "side_above_3away": lambda k0, k1: (
#         k0.hand == k1.hand
#         and (k0.finger, k1.finger) == (1, 4)
#         and k0.v_dist != k1.v_dist
#         # ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 3 and k0.v_dist > k1.v_dist
#     ),  # 💡 It's index and little finger. This rule is questionable.
#     "index_above": lambda k0, k1: (
#         k0.finger == 1
#         and k0.v_dist > 0
#         and (k1.hand != k0.hand or k0 == k1 or k1.v_dist < k0.v_dist)
#     ),
#     "middle_above_ring": lambda k0, k1: (
#         k0.hand == k1.hand
#         and (k0.finger, k1.finger) == (2, 3)
#         and k0.v_dist > k1.v_dist
#     ),  # 💡 Not an issue for me?
#     "ring_above_middle": lambda k0, k1: (
#         k0.hand == k1.hand
#         and (k0.finger, k1.finger) == (2, 3)
#         and k0.v_dist < k1.v_dist
#     ),
# }

# ignore_penalties: list[str] = ["shorter_above"]


# def penalty_application_str(flow_matrix: NDArray) -> str:
#     char = lambda x: "·" if x == 1 else "█"
#     s: list[list[float]] = flow_matrix.tolist()  # type: ignore
#     return "\n".join("".join(map(char, l)) for l in s)


# def application_mismatch_str(expected: NDArray, obtained: NDArray) -> str:
#     applied_str: Callable[[float], str] = lambda x: "█" if x < 1 else "·"
#     diff_str: Callable[[float], str] = lambda x: (
#         "\033[42m+\033[0m" if x < 0 else "\033[41m-\033[0m" if x > 0 else "·"
#     )
#     exp: NDArray = np.vectorize(applied_str)(expected)
#     obt: NDArray = np.vectorize(applied_str)(obtained)
#     diff: NDArray = np.vectorize(diff_str)(obtained - expected)
#     n = exp.shape[1]
#     lines = [f"{"Expected:":{n}}   {"Got:":{n}}   {"Diff:":{n}}"]
#     for i, mat_lines in enumerate(zip(exp, obt, diff)):
#         lines.append(
#             f"{"   ".join(
#             "".join(line) for line in mat_lines
#         )}   {i+1}"
#         )
#     for k in [0, 1]:
#         d = [f"{i} "[k] for i in range(1, n + 1)]
#         lines.append("   ".join(["".join(d)] * 3))
#     d = [str(i)[0] for i in range(1, n + 1)]
#     return "\n".join(lines)


# def expected_with_penalty(penalty: str) -> NDArray:
#     args = {a: 1.0 for a in flow_args}
#     args[penalty] = 0.5
#     expected = flow_matrix(**args)
#     return expected


# def check_no_penalties() -> None:
#     for penalty in no_penalties:
#         expected = expected_with_penalty(penalty)
#         assert np.all(expected == 1)


# def check_key_penalties() -> None:
#     for penalty, condition in key_penalties.items():
#         expected = expected_with_penalty(penalty)
#         s = np.array([[int(condition(k)) for k in keys]])
#         s = s + s.T
#         s = 0.5**s
#         assert np.array_equal(s, expected)


# def check_pair_penalties() -> None:
#     for penalty_col, symmetry in ((pair_penalties, False), (sym_pair_penalties, True)):
#         for penalty, condition in penalty_col.items():
#             expected = expected_with_penalty(penalty)
#             s = np.array([[int(condition(k0, k1)) for k1 in keys] for k0 in keys])
#             if symmetry:
#                 s += np.array([[int(condition(k1, k0)) for k1 in keys] for k0 in keys])
#             s = 0.5**s
#             if not np.array_equal(s, expected):
#                 assert np.array_equal(
#                     s[:24, :24], expected[:24, :24]
#                 ), f"{penalty}:\n\n{application_mismatch_str(expected,s)}"
#                 descr = (
#                     "\n" + application_mismatch_str(expected, s)
#                     if _VERBOSE_WARNING
#                     else ""
#                 )
#                 print(
#                     f"\033[93m⚠ \033[92m{penalty}\033[93m: Mismatch for 32 keys\033[0m{descr}"
#                 )


# def report_uncovered_penalties():
#     uncovered = set(flow_args)
#     for penalty_col in (
#         no_penalties,
#         key_penalties,
#         pair_penalties,
#         sym_pair_penalties,
#         ignore_penalties,
#     ):
#         uncovered -= set(penalty_col)
#     if not uncovered:
#         print("\nAll penalties covered. ✅\n")
#         return
#     print("\nUncovered penalties:\n" + "".join(f"   {p}\n" for p in uncovered))


# # _VERBOSE_WARNING = True
# check_no_penalties()
# check_key_penalties()
# check_pair_penalties()
# report_uncovered_penalties()

# """
# Regarding mismatches with original 32×32 flow matrices:
# - outward:
#     Original implementation mistakenly ignored side keys.
# - skip_row_1away:
#     Original implementation mistakenly included 4↔27 (L1↑↔L1↘) and 13↔30 (R1↑↔R1↙)
#     (which are already included in skip_row_0away!),
#     instead of 4↔27 (L2↑↔L1↘) and 14↔30 (R2↑↔R1↙).
# - skip_row_2away:
#     Original implementation forgot 2↔27 (L3↑↔L1↘) and 15↔30 (R3↑↔R1↙)
#     (while 10↔25 (L3↓↔L1↗) and 23↔28 (R3↓↔R1↖) are included!).
# - skip_row_3away:
#     Original implementation forgot 1↔27 (L4↑↔L1↘)
#     (while 9↔25 (L4↓↔L1↗) and 16↔30 (R4↑↔R1↙) are included!).
# We also ignore:
# - shorter_above:
#     It is very badly defined, and covered through more accurate penalties.
# """

# > ---------

""" yaml
ANSI:
  geometry: |
    1 1 1 1 1 1 1 1 1 1 1 1 1 2
    1.5 1 1 1 1 1 1 1 1 1 1 1 1 1.5
    1.75 1 1 1 1 1 1 1 1 1 1 1 2.25
    2.25 1 1 1 1 1 1 1 1 1 1 2.75
    1.25 1.25 1.25 6.25 1.25 1.25 1.25 1.25
  fingers: | # "*"" = home keys (⚠ as programmed, only the line it's used in is detected)
    L4  L4  L4  L3  L2  L1  L1  R1  R1  R2  R3  R4  R4  R4
    L4   L4  L3  L2  L1  L1  R1  R1  R2  R3  R4  R4  R4  R4
    L4    L4* L3* L2* L1* L1  R1  R1* R2* R3* R4* R4  R4
    L4     L4  L3  L2  L1  L1  R1  R1  R2  R3  R4  R4
    L4   -   LT             RT            RT  -   -   -
  layout: |
    `~ 1! 2@ 3# 4$ 5% 6^ 7& 8* 9( 0) -_ =+ ※
    ↹ q w e r t y u i o p [{ ]} \\|
    ※ a s d f g h j k l ;: '" ↵
    ⇫ z x c v b n m ,< .> /? ⇫
    ⋉ ⊞ ⋊ ‿ ⋈ ※ ※ ※
  engram_id: | # was only useful for comparison
    - -  -  -  -  -  -  -  -  -  -  -  -  - 
    - 1  2  3  4  25 28 13 14 15 16 31 - - 
    -  5  6  7  8  26 29 17 18 19 20 32 - 
    -   9  10 11 12 27 30 21 22 23 24 - 
    -  -  -          -         -  -  - -
"""
