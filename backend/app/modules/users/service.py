from sqlalchemy.orm import Session

from app.shared.models.user import User, UserProfile


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user

    def update_profile(self, user_id: str, nome: str = None, telefone: str = None) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Usuário não encontrado")
        if nome:
            user.nome = nome
        if telefone is not None:
            user.telefone = telefone
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def update_profile_details(self, user_id: str, **kwargs) -> UserProfile:
        profile = self.get_or_create_profile(user_id)
        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
