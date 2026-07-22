# Модель для счетов транзакций
from sqlalchemy import Column, Integer, String
from db_models.user import Base


class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)
