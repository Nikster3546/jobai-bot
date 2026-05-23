from datetime import datetime
from sqlalchemy import BigInteger, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(32))      # apply | rewrite | interview
    vacancy_title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Резюме НЕ логируем — персональные данные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)