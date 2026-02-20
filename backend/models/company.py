from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, default="UAE")  # UAE, KSA
    industry = Column(String, nullable=True)
    currency = Column(String, default="AED")
    fiscal_year_end = Column(String, default="December")
    tax_registration = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="company")
    uploads = relationship("Upload", back_populates="company")
    account_mappings = relationship("AccountMapping", back_populates="company")
    trial_balance_entries = relationship("TrialBalanceEntry", back_populates="company")
