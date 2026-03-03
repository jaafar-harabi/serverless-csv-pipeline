from typing import Dict, List

from .models import Transaction
from .readers import err, read_accounts, read_clients, read_portfolios, read_transactions


def process_day(
   clients_csv: str,
   portfolios_csv: str,
   accounts_csv: str,
   transactions_csv: str,
) -> List[dict]:
   """
   Returns JSON-serializable message dicts:
     - one client_message per client
     - one portfolio_message per portfolio
     - any number of error_message for malformed inputs / missing references
   Output ordering is deterministic (sorted by references).
   """
   messages: List[dict] = []

   clients, e1 = read_clients(clients_csv)
   portfolios, e2 = read_portfolios(portfolios_csv)
   accounts, e3 = read_accounts(accounts_csv)
   transactions, e4 = read_transactions(transactions_csv)
   messages.extend(e1 + e2 + e3 + e4)

   # Index transactions by account for fast lookup
   txs_by_account: Dict[str, List[Transaction]] = {}
   for tx in transactions:
       txs_by_account.setdefault(tx.account_number, []).append(tx)

   # Aggregate taxes paid per client (via portfolio -> account)
   client_taxes_sum: Dict[str, float] = {cref: 0.0 for cref in clients.keys()}

   for pref in sorted(portfolios.keys()):
       p = portfolios[pref]
       if not p.account_number:
           continue

       acct = accounts.get(p.account_number)
       if acct is None:
           messages.append(err(p.client_reference, pref, f"account_number {p.account_number} not found in accounts"))
           continue

       if p.client_reference not in clients:
           messages.append(err(p.client_reference, pref, f"client_reference {p.client_reference} not found in clients"))
           continue

       client_taxes_sum[p.client_reference] += acct.taxes_paid

   # Portfolio messages (one per portfolio)
   for pref in sorted(portfolios.keys()):
       p = portfolios[pref]
       acct = accounts.get(p.account_number) if p.account_number else None

       if p.account_number and acct is None:
           messages.append(err(p.client_reference, pref, f"account_number {p.account_number} not found in accounts"))

       txs = txs_by_account.get(p.account_number, []) if p.account_number else []
       num_txs = len(txs)

       # Deposits are strictly defined by keyword == "DEPOSIT" to match spec and avoid misclassification.
       sum_deposits = sum(t.amount for t in txs if t.keyword.upper() == "DEPOSIT")

       cash_balance = acct.cash_balance if acct else 0.0
       messages.append(
           {
               "type": "portfolio_message",
               "portfolio_reference": pref,
               "cash_balance": int(cash_balance) if float(cash_balance).is_integer() else cash_balance,
               "number_of_transactions": num_txs,
               "sum_of_deposits": int(sum_deposits) if float(sum_deposits).is_integer() else sum_deposits,
           }
       )

   # Client messages (one per client)
   for cref in sorted(clients.keys()):
       c = clients[cref]
       taxes_paid = client_taxes_sum.get(cref, 0.0)
       messages.append(
           {
               "type": "client_message",
               "client_reference": cref,
               "tax_free_allowance": c.tax_free_allowance,
               "taxes_paid": int(taxes_paid) if float(taxes_paid).is_integer() else taxes_paid,
           }
       )

   return messages
