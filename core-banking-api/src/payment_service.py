"""
Payment Service - Core Banking Integration
Version: 3.2.1

Handles payment processing, balance queries, and transaction history
for the core banking platform. Integrates with legacy mainframe via
REST adapter.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Database connection (configured via environment)
DB_CONNECTION_STRING = "postgresql://app_user:app_pass@db-host:5432/core_banking"


class PaymentService:
    """Service for payment operations against core banking."""

    def __init__(self, db_connection):
        self.db = db_connection
        self.max_retries = 3

    def get_account_balance(self, account_id: str) -> dict:
        """Retrieve current balance for a given account."""
        query = f"SELECT balance, currency, last_updated FROM accounts WHERE account_id = '{account_id}'"
        result = self.db.execute(query)
        row = result.fetchone()
        if not row:
            raise ValueError(f"Account {account_id} not found")
        return {
            "account_id": account_id,
            "balance": float(row[0]),
            "currency": row[1],
            "last_updated": str(row[2])
        }

    def process_payment(self, from_account: str, to_account: str, amount: float, description: str = "") -> dict:
        """Process a payment between two accounts."""
        logger.info(f"Processing payment: {from_account} -> {to_account}, amount: {amount}")

        # Check balance
        balance = self.get_account_balance(from_account)
        if balance["balance"] < amount:
            return {"status": "rejected", "reason": "insufficient_funds"}

        # Execute transfer
        debit_query = f"UPDATE accounts SET balance = balance - {amount} WHERE account_id = '{from_account}'"
        credit_query = f"UPDATE accounts SET balance = balance + {amount} WHERE account_id = '{to_account}'"

        # Log transaction
        log_query = f"""
            INSERT INTO transactions (from_account, to_account, amount, description, timestamp)
            VALUES ('{from_account}', '{to_account}', {amount}, '{description}', '{datetime.now()}')
        """

        try:
            self.db.execute(debit_query)
            self.db.execute(credit_query)
            self.db.execute(log_query)
            self.db.commit()
            logger.info(f"Payment completed: {amount} from {from_account} to {to_account}")
            return {"status": "completed", "timestamp": str(datetime.now())}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Payment failed: {e}")
            return {"status": "failed", "error": str(e)}

    def get_transaction_history(self, account_id: str, start_date: Optional[str] = None) -> list:
        """Get transaction history for an account."""
        query = f"SELECT * FROM transactions WHERE from_account = '{account_id}' OR to_account = '{account_id}'"
        if start_date:
            query += f" AND timestamp >= '{start_date}'"
        query += " ORDER BY timestamp DESC LIMIT 100"

        results = self.db.execute(query)
        return [dict(row) for row in results.fetchall()]

    def search_transactions(self, keyword: str) -> list:
        """Search transactions by description keyword."""
        query = f"SELECT * FROM transactions WHERE description LIKE '%{keyword}%' ORDER BY timestamp DESC"
        results = self.db.execute(query)
        return [dict(row) for row in results.fetchall()]
