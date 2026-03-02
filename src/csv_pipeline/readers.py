import csv
from typing import Dict, List, Optional, Tuple

from .models import Account, Client, Portfolio, Transaction


def _to_int(v: str) -> int:
   return int(v.strip())


def _to_float(v: str) -> float:
   return float(v.strip())


def err(client_ref: Optional[str], portfolio_ref: Optional[str], message: str) -> dict:
   return {
       "type": "error_message",
       "client_reference": client_ref,
       "portfolio_reference": portfolio_ref,
       "message": message,
   }


def read_clients(path: str) -> Tuple[Dict[str, Client], List[dict]]:
   errors: List[dict] = []
   clients: Dict[str, Client] = {}

   with open(path, newline="", encoding="utf-8") as f:
       reader = csv.DictReader(f)
       required = {"client_reference", "tax_free_allowance"}
       if not required.issubset(reader.fieldnames or []):
           return {}, [err(None, None, f"clients CSV missing columns: {sorted(required)}")]

       for i, row in enumerate(reader, start=2):
           try:
               cref = (row.get("client_reference") or "").strip()
               if not cref:
                   raise ValueError("empty client_reference")
               tfa = _to_int(row["tax_free_allowance"])
               clients[cref] = Client(client_reference=cref, tax_free_allowance=tfa)
           except Exception as e:
               errors.append(err(None, None, f"clients row {i}: {e}"))

   return clients, errors


def read_portfolios(path: str) -> Tuple[Dict[str, Portfolio], List[dict]]:
   errors: List[dict] = []
   portfolios: Dict[str, Portfolio] = {}

   with open(path, newline="", encoding="utf-8") as f:
       reader = csv.DictReader(f)
       required = {"portfolio_reference", "client_reference"}
       if not required.issubset(reader.fieldnames or []):
           return {}, [err(None, None, f"portfolios CSV missing columns: {sorted(required)}")]

       has_acc = "account_number" in (reader.fieldnames or [])

       for i, row in enumerate(reader, start=2):
           try:
               pref = (row.get("portfolio_reference") or "").strip()
               cref = (row.get("client_reference") or "").strip()
               if not pref or not cref:
                   raise ValueError("empty portfolio_reference or client_reference")

               acc = (row.get("account_number") or "").strip() if has_acc else ""
               if not has_acc:
                   errors.append(err(cref, pref, "portfolios CSV missing account_number column"))

               portfolios[pref] = Portfolio(
                   portfolio_reference=pref,
                   client_reference=cref,
                   account_number=(acc or None),
               )
           except Exception as e:
               errors.append(err(None, None, f"portfolios row {i}: {e}"))

   return portfolios, errors


def read_accounts(path: str) -> Tuple[Dict[str, Account], List[dict]]:
   errors: List[dict] = []
   accounts: Dict[str, Account] = {}

   with open(path, newline="", encoding="utf-8") as f:
       reader = csv.DictReader(f)
       required = {"account_number", "cash_balance", "currency", "taxes_paid"}
       if not required.issubset(reader.fieldnames or []):
           return {}, [err(None, None, f"accounts CSV missing columns: {sorted(required)}")]

       for i, row in enumerate(reader, start=2):
           try:
               acc = (row.get("account_number") or "").strip()
               if not acc:
                   raise ValueError("empty account_number")

               cash = _to_float(row["cash_balance"])
               cur = (row.get("currency") or "").strip()
               taxes = _to_float(row["taxes_paid"])

               accounts[acc] = Account(
                   account_number=acc,
                   cash_balance=cash,
                   currency=cur,
                   taxes_paid=taxes,
               )
           except Exception as e:
               errors.append(err(None, None, f"accounts row {i}: {e}"))

   return accounts, errors


def read_transactions(path: str) -> Tuple[List[Transaction], List[dict]]:
   errors: List[dict] = []
   txs: List[Transaction] = []

   with open(path, newline="", encoding="utf-8") as f:
       reader = csv.DictReader(f)
       required = {"account_number", "transaction_reference", "amount", "keyword"}
       if not required.issubset(reader.fieldnames or []):
           return [], [err(None, None, f"transactions CSV missing columns: {sorted(required)}")]

       for i, row in enumerate(reader, start=2):
           try:
               acc = (row.get("account_number") or "").strip()
               tref = (row.get("transaction_reference") or "").strip()
               if not acc or not tref:
                   raise ValueError("empty account_number or transaction_reference")

               amt = _to_float(row["amount"])
               kw = (row.get("keyword") or "").strip()

               txs.append(
                   Transaction(
                       account_number=acc,
                       transaction_reference=tref,
                       amount=amt,
                       keyword=kw,
                   )
               )
           except Exception as e:
               errors.append(err(None, None, f"transactions row {i}: {e}"))

   return txs, errors
