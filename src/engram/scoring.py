from typing import Callable, Literal

# > Building key data from descriptions in YAML


class Key:
    hand: Literal["L", "R"]
    finger: Literal[0, 1, 2, 3, 4]
    dx: int  # horizontal distance from rest position, > 0 ⇔ inward
    dy: int  # vertical   distance from rest position, > 0 ⇔ upward

    def __init__(self, finger: str, dx: int, dy: int) -> None:
        # IMPROVE Support e.g. Key("L1↗") as alternative to Key("L1",1,1)
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
        return f"{self.hand}{self.finger or 'T'}{self.__movement()}"

    def __movement(self) -> str:
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


class KeyPenalty:
    name: str
    cost: float
    __condition: Callable[[Key], bool]
    # ▲ Needs to be private
    # - Implementation can change for str representation and parsing purposes
    # - For interkey, the “true condition” is affected by symmetry option that
    #   should be split for GUI purposes.
    # IMPROVE This comment should become irrelevant

    def __init__(
        self,
        condition: Callable[[Key], bool],
        cost: float,
        *,
        name: str = "",
    ) -> None:
        self.__condition = condition
        self.cost = cost
        self.name = name

    def applies(self, key: Key) -> bool:
        return self.__condition(key)


class InterKeyPenalty:
    name: str
    __condition: Callable[[Key, Key], bool]
    cost: float
    symmetrical: bool
    same_hand: bool

    def __init__(
        self,
        condition: Callable[[Key, Key], bool],
        cost: float,
        *,
        name: str = "",
        symmetrical: bool = False,
        same_hand: bool = True,
    ) -> None:
        self.__condition = condition
        self.cost = cost
        self.name = name
        self.symmetrical = symmetrical
        self.same_hand = same_hand

    def applies(self, key_0: Key, key_1: Key) -> bool:
        if self.same_hand and key_0.hand != key_1.hand:
            return False
        if self.__condition(key_0, key_1):
            return True
        return self.symmetrical and self.__condition(key_1, key_0)
