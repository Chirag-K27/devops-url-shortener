from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String(2048), nullable=False, index=True)
    short_code = Column(String(10), unique=True, nullable=False, index=True)
    click_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<URL(short_code={self.short_code}, clicks={self.click_count})>"
