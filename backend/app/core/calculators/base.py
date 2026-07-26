from abc import ABC, abstractmethod


class BaseCalculator(ABC):
   

    @abstractmethod
    def calculate(self) -> dict:
        ...