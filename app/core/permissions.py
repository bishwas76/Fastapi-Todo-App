from fastapi import Request, HTTPException, status
from abc import ABC, abstractmethod

class BasePermission(ABC):
    """Base class for defining permissions in the application. 
    This class should be inherited by specific permission classes that implement the has_permission method."""

    @abstractmethod
    def has_permission(self, request: Request) -> bool:
        pass

    def __call__(self):
        """
        Allows the permission class to be used as a dependency in FastAPI routes.
        """
        def dependency(request: Request):
            if not self.has_permission(request):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action.",
                )
        return dependency

class IsAuthenticated(BasePermission):
    """Permission class that checks if the user is authenticated."""

    def has_permission(self, request: Request) -> bool:
        return hasattr(request.state, "user") and request.state.user is not None

class AllowAny(BasePermission):
    """Permission class that allows access to any user, regardless of authentication status."""

    def has_permission(self, request: Request) -> bool:
        return True