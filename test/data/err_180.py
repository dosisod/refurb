import abc
from abc import ABCMeta, ABC, abstractmethod


class Dummy:
    pass

# these will match

class Animal(metaclass=ABCMeta):
    @abstractmethod
    def speak(self) -> None: ...


class Computer(metaclass=abc.ABCMeta):
    @abstractmethod
    def compute(self) -> None: ...


# these will not

class Vehicle(ABC):
    @abstractmethod
    def move(self) -> None: ...


class Human(Animal):
    name: str
