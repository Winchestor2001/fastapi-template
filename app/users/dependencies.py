from app.user.repositories import UserRepository
from app.user.services import UserService


def get_user_service():
    user_repo = UserRepository()
    return UserService(user_repo)