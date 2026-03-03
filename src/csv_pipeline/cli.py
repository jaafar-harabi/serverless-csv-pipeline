import json
import sys

from .processor import process_day


def main(argv: list[str]) -> int:
   """
   Usage:
     python -m csv_pipeline.cli <clients.csv> <portfolios.csv> <accounts.csv> <transactions.csv>

   Prints JSON Lines to stdout.
   """
   if len(argv) != 5:
       print(
           "Usage: python -m csv_pipeline.cli <clients.csv> <portfolios.csv> <accounts.csv> <transactions.csv>",
           file=sys.stderr,
       )
       return 2

   msgs = process_day(argv[1], argv[2], argv[3], argv[4])
   for m in msgs:
       print(json.dumps(m, ensure_ascii=False))
   return 0


if __name__ == "__main__":
   raise SystemExit(main(sys.argv))
