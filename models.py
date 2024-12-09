from datetime import datetime

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Dictionary(Base):
    __tablename__ = "dictionary"

    dictionary_id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String(length=100), nullable=False)
    english_word = sq.Column(sq.String(length=100), nullable=False)
    user_added = sq.Column(sq.BIGINT, nullable=False)

    def __repr__(self):
        return f"{self.dictionary_id}, {self.russian_word}, {self.english_word}, {self.user_added}"


class User(Base):
    __tablename__ = "user"

    user_id = sq.Column(sq.BIGINT, primary_key=True, autoincrement=False)
    create_date = sq.Column(sq.DateTime, default=datetime.now)

    def __repr__(self):
        return f"{self.user_id}, {self.create_date}"


class UserDictionary(Base):
    __tablename__ = "user_dictionary"

    user_dictionary_id = sq.Column(sq.Integer, primary_key=True)
    dictionary_id = sq.Column(sq.Integer, sq.ForeignKey("dictionary.dictionary_id", ondelete="CASCADE"), nullable=False)
    user_id = sq.Column(sq.BIGINT, sq.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)

    dictionary = relationship(Dictionary, backref="user_dictionary_1")
    user = relationship(User, backref="user_dictionary_2")

    def __repr__(self):
        return f"{self.user_dictionary_id}, {self.dictionary_id}, {self.user_id}"
