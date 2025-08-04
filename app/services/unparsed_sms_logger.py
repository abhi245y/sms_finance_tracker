import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class UnparsedSMSLogger:
    """
    Logs finance-related SMS messages that couldn't be parsed by any parser.
    Helps identify missing bank/service patterns that need new parsers.
    """
    
    def __init__(self):
        self.log_dir = Path("logs/unparsed_sms")
        self.max_file_size_mb = 5
        
        self.finance_keywords = [
            r'\brs\.?\s*\d+', r'₹\s*\d+', r'\$\s*\d+', r'\binr\b', r'\busd\b',
            r'\brupees?\b', r'\bamount\b', r'\bbalance\b',
            
            r'\bdebit(ed)?\b', r'\bcredit(ed)?\b', r'\bspent\b', r'\bpaid\b', 
            r'\btransaction\b', r'\btransfer(red)?\b', r'\bpayment\b',
            r'\bwithdrawn?\b', r'\bdeposit(ed)?\b', r'\bpurchase\b', r'\brefund\b',
            r'\bcashback\b', r'\brecharge\b', r'\bbill\b',
            
            r'\bbank\b', r'\bcard\b', r'\baccount\b', r'\ba/c\b', r'\bwallet\b',
            r'\bupi\b', r'\bneft\b', r'\brtgs\b', r'\bimps\b', r'\batm\b',
            
            r'\bpaytm\b', r'\bphonepe\b', r'\bgooglepay\b', r'\bgpay\b',
            r'\bamazonpay\b', r'\bmobikwik\b', r'\bfreecharge\b',
            
            r'\bhdfc\b', r'\bicici\b', r'\bsbi\b', r'\baxis\b', r'\bkotak\b',
            r'\byes bank\b', r'\bindusind\b', r'\bpnb\b', r'\biob\b', r'\bcanara\b',
            r'\bfederal\b', r'\bidfc\b', r'\bamex\b', r'\bamerican express\b',
            
            r'\bsuccessful(ly)?\b', r'\bfailed\b', r'\bdeclined\b', r'\bapproved\b',
            r'\bcompleted\b', r'\bprocessed\b'
        ]
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def is_finance_related(self, sms_text: str) -> bool:
        """
        Check if the SMS text contains finance-related keywords.
        Uses regex patterns for more accurate matching.
        """
        if not sms_text:
            return False
            
        text_lower = sms_text.lower()
        
        for pattern in self.finance_keywords:
            if re.search(pattern, text_lower):
                return True
                
        return False
    
    def _get_current_log_file(self) -> Path:
        """Get the current log file path with date-based naming."""
        today = datetime.now()
        filename = f"unparsed_finance_sms_{today.strftime('%Y_%m_%d')}.log"
        return self.log_dir / filename
    
    def _should_rotate_file(self, file_path: Path) -> bool:
        """Check if file should be rotated based on size."""
        if not file_path.exists():
            return False
            
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        return file_size_mb >= self.max_file_size_mb
    
    def _get_rotated_filename(self, original_path: Path) -> Path:
        """Generate a rotated filename with timestamp."""
        timestamp = datetime.now().strftime('%H%M%S')
        stem = original_path.stem
        suffix = original_path.suffix
        return original_path.parent / f"{stem}_{timestamp}{suffix}"
    
    def log_unparsed_sms(self, sms_text: str, source_info: Optional[str] = None) -> None:
        """
        Log an unparsed finance-related SMS to file.
        
        Args:
            sms_text: The SMS content that couldn't be parsed
            source_info: Optional additional info about the source (e.g., sender ID)
        """
        if not self.is_finance_related(sms_text):
            return
            
        current_file = self._get_current_log_file()
        
        if self._should_rotate_file(current_file):
            rotated_file = self._get_rotated_filename(current_file)
            try:
                current_file.rename(rotated_file)
                print(f"DEBUG: Rotated unparsed SMS log to {rotated_file.name}")
            except OSError as e:
                print(f"WARNING: Could not rotate log file: {e}")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        separator = "=" * 80
        
        log_entry = f"""
{separator}
TIMESTAMP: {timestamp}
SOURCE: {source_info or 'Unknown'}
SMS CONTENT:
{sms_text}
{separator}

"""
        
        try:
            with open(current_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(f"DEBUG: Logged unparsed finance SMS to {current_file.name}")
        except OSError as e:
            print(f"ERROR: Could not write to unparsed SMS log: {e}")
    
    def get_recent_unparsed_count(self, days: int = 7) -> int:
        """
        Get count of unparsed SMS entries from recent days.
        Useful for monitoring how many transactions might be missed.
        """
        count = 0
        try:
            for log_file in self.log_dir.glob("unparsed_finance_sms_*.log"):
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    count += content.count("=" * 80) // 2 
        except OSError as e:
            print(f"WARNING: Could not read unparsed SMS logs: {e}")
            
        return count
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """
        Clean up log files older than specified days.
        Should be called periodically to prevent disk space issues.
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for log_file in self.log_dir.glob("unparsed_finance_sms_*.log"):
                file_date_str = log_file.stem.split('_')[-3:]  
                if len(file_date_str) == 3:
                    try:
                        file_date = datetime.strptime('_'.join(file_date_str), '%Y_%m_%d')
                        if file_date < cutoff_date:
                            log_file.unlink()
                            print(f"DEBUG: Cleaned up old unparsed SMS log: {log_file.name}")
                    except ValueError:
                        continue
        except OSError as e:
            print(f"WARNING: Error during log cleanup: {e}")