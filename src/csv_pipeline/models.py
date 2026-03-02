from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Client:
   client_reference: str
   tax_free_allowance: int


@dataclass(frozen=True)
class Portfolio:
   portfolio_reference: str
   client_reference: str
   account_number: Optional[str]


@dataclass(frozen=True)
class Account:
   account_number: str
   cash_balance: float
   currency: str
   taxes_paid: float


@dataclass(frozen=True)
class Transaction:
   account_number: str
   transaction_reference: str
   amount: float
   keyword: str
