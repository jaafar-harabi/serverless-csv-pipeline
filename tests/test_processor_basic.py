from csv_pipeline.processor import process_day


def test_basic_happy_path(tmp_path):
   (tmp_path / "clients.csv").write_text("client_reference,tax_free_allowance\nC1,801\n", encoding="utf-8")
   (tmp_path / "portfolios.csv").write_text(
       "portfolio_reference,client_reference,account_number\nP1,C1,A1\n", encoding="utf-8"
   )
   (tmp_path / "accounts.csv").write_text(
       "account_number,cash_balance,currency,taxes_paid\nA1,15000,EUR,0\n", encoding="utf-8"
   )
   (tmp_path / "transactions.csv").write_text(
       "account_number,transaction_reference,amount,keyword\nA1,T1,5000,DEPOSIT\nA1,T2,-200,WITHDRAWAL\n",
       encoding="utf-8",
   )

   msgs = process_day(
       str(tmp_path / "clients.csv"),
       str(tmp_path / "portfolios.csv"),
       str(tmp_path / "accounts.csv"),
       str(tmp_path / "transactions.csv"),
   )

   assert msgs[0]["type"] == "portfolio_message"
   assert msgs[0]["portfolio_reference"] == "P1"
   assert msgs[0]["cash_balance"] == 15000
   assert msgs[0]["number_of_transactions"] == 2
   assert msgs[0]["sum_of_deposits"] == 5000

   assert msgs[1]["type"] == "client_message"
   assert msgs[1]["client_reference"] == "C1"
   assert msgs[1]["tax_free_allowance"] == 801
   assert msgs[1]["taxes_paid"] == 0


def test_missing_account_generates_error(tmp_path):
   (tmp_path / "clients.csv").write_text("client_reference,tax_free_allowance\nC1,801\n", encoding="utf-8")
   (tmp_path / "portfolios.csv").write_text(
       "portfolio_reference,client_reference,account_number\nP1,C1,AX\n", encoding="utf-8"
   )
   (tmp_path / "accounts.csv").write_text("account_number,cash_balance,currency,taxes_paid\n", encoding="utf-8")
   (tmp_path / "transactions.csv").write_text("account_number,transaction_reference,amount,keyword\n", encoding="utf-8")

   msgs = process_day(
       str(tmp_path / "clients.csv"),
       str(tmp_path / "portfolios.csv"),
       str(tmp_path / "accounts.csv"),
       str(tmp_path / "transactions.csv"),
   )

   assert any(m["type"] == "error_message" for m in msgs)
   assert any(m.get("portfolio_reference") == "P1" for m in msgs if m["type"] == "error_message")
