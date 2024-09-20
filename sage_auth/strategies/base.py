from abc import ABC, abstractmethod

class AuthStrategy(ABC):
    @abstractmethod
    def validate(self, user_data):
        """Validates user data (email, phone, etc.)."""
        pass

    # @abstractmethod
    # def authenticate(self, user_data):
    #     """Handles user authentication logic."""
    #     pass
