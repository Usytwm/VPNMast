from abc import ABC, abstractmethod
class user_crud_interface(ABC):
    @abstractmethod
    def create_user(self, user):
        pass
    @abstractmethod
    def save_users(self):
        pass
    @abstractmethod
    def delete_user(self, user):
        pass
    @abstractmethod
    def show_users(self):
        pass
