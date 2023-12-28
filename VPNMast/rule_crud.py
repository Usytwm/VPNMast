from abc import ABC, abstractmethod
class rule_crud_interface(ABC):
    @abstractmethod
    def create_rule(self, rule):
        pass
    @abstractmethod
    def save_rules(self):
        pass
    @abstractmethod
    def delete_rule(self, rule):
        pass
    @abstractmethod
    def show_rules(self):
        pass
