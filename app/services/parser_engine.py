from typing import Dict, Optional, Any, List

from sqlalchemy.orm import Session

from app.crud import crud_account
from app.schemas.account import AccountCreate
from app.models.account import AccountType

from .parsers.base_parser import BaseParser
from .parsers.hdfc_parser import HDFCParser
from .parsers.federal_parser import FederalBankParser
from .parsers.amex_parser import AmexParser
from .parsers.sbi_parser import SBIParser
from .parsers.icici_parser import ICICIBankParser
from .parsers.idfc_parser import IDFCFirstBankParser

from app.core.hashing import generate_transaction_hash

class ParserEngine:
    def __init__(self, db_session: Session):
        """
        The engine is initialized with a database session to be able to resolve accounts.
        """
        self.db: Session = db_session
        
        self.parsers: List[BaseParser] = [
            HDFCParser(),
            FederalBankParser(),
            AmexParser(),
            SBIParser(),
            ICICIBankParser(),
            IDFCFirstBankParser(),
        ]
        self._credit_keywords = ["credited to", "credited to your a/c", "credited to acct", "received", "deposited"]
        self._debit_keywords = ["debited", "spent", "sent from", "debited"]
        
    def _get_flow_type(self, sms_text: str) -> Optional[str]:
        """Determines if the SMS is a credit, debit, or unknown transaction."""
        sms_lower = sms_text.lower()
        if any(keyword in sms_lower for keyword in self._credit_keywords):
            return "CREDIT"
        if any(keyword in sms_lower for keyword in self._debit_keywords):
            return "DEBIT"
        return None

    def _resolve_account_id(self, parsed_data: Dict[str, Any]) -> Optional[int]:
        """
        Takes parsed data and finds or creates an account, returning the account_id.
        Returns None if the account is ambiguous (e.g., last4 is None).
        """
        bank_name = parsed_data.get("bank_name")
        account_last4 = parsed_data.get("account_last4")
        
        if not account_last4:
            print(f"DEBUG: Ambiguous account for {bank_name}. Requires user selection.")
            return None

        account = crud_account.get_account_by_identifier(
            self.db, bank_name=bank_name, account_last4=account_last4
        )

        if account:
            print(f"DEBUG: Found existing account: ID {account.id} ({account.name})")
            return account.id

        print(f"DEBUG: No existing account found for {bank_name} ending in {account_last4}. Creating placeholder.")
        placeholder_name = f"New Account - {bank_name} {account_last4}"
        
        account_in = AccountCreate(
            name=placeholder_name,
            account_type=AccountType.UNKNOWN,
            bank_name=bank_name,
            account_last4=account_last4
        )
        new_account = crud_account.create_account(self.db, obj_in=account_in)
        print(f"DEBUG: Created placeholder account: ID {new_account.id} ({new_account.name})")
        # Code to trigger a notification to the user here in the future TODO Telegram Bot/UI
        
        return new_account.id


    def run(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """
        The main public method to run the full parsing and account resolution pipeline.
        
        Returns a dictionary ready for transaction creation, or None if the SMS should be ignored.
        The dictionary will include 'account_id' if an account could be resolved.
        """
        flow_type = self._get_flow_type(sms_text)
        
        if not flow_type:
            print(f"DEBUG: Could not determine flow type (credit/debit). Ignoring SMS: {sms_text[:70]}...")
            return None
        
        if flow_type == "CREDIT":
            print(f"DEBUG: Ignoring credit transaction for now: {sms_text[:70]}...")
            return None

        parsed_data: Optional[Dict[str, Any]] = None
        for parser in self.parsers:
            if (result := parser.parse(sms_text)):
                parsed_data = result
                print(f"DEBUG: SMS structure parsed by {parser.__class__.__name__}")
                break
        
        if not parsed_data:
            print(f"DEBUG: No parser matched for spend SMS: {sms_text[:70]}...")
            return None
        
        original_bank_name = parsed_data.get("bank_name")

        account_id = self._resolve_account_id(parsed_data)
        parsed_data["account_id"] = account_id
        
        if not account_id:
            parsed_data["bank_name"] = original_bank_name
            
        unique_hash = generate_transaction_hash(parsed_data)
        if not unique_hash:
            print("ERROR: Could not generate a stable hash, ignoring transaction.", parsed_data)
            return None
        
        parsed_data["unique_hash"] = unique_hash
        parsed_data.setdefault("currency", "INR")
        
        parsed_data["account_id"] = account_id
        parsed_data["flow_type"] = flow_type
        
        parsed_data.pop("bank_name", None)
        parsed_data.pop("account_last4", None)

        return parsed_data