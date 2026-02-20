from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class MasterAccount(Base):
    """Pre-built IFRS-based master chart of accounts."""
    __tablename__ = "master_accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    sub_category = Column(String, nullable=True)  # Current Asset, Non-Current Asset, etc.
    fs_line = Column(String, nullable=True)  # Financial statement line item
    normal_balance = Column(String, default="debit")  # debit or credit


class AccountMapping(Base):
    """Maps company-specific accounts to IFRS master accounts."""
    __tablename__ = "account_mappings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    source_code = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    source_type = Column(String, nullable=True)  # Type from uploaded file (Bank, Fixed Asset, etc.)
    master_account_id = Column(Integer, ForeignKey("master_accounts.id"), nullable=True)
    is_mapped = Column(Boolean, default=False)
    mapped_by = Column(String, default="auto")  # auto or manual
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="account_mappings")
    master_account = relationship("MasterAccount")
