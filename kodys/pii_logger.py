# -*- coding: utf-8 -*-
import re
import logging

class PIIMaskingFilter(logging.Filter):
    """
    Logging filter that masks PII (Personally Identifiable Information) in log records.
    Redacts:
    - Email addresses
    - Phone numbers (10+ digits)
    - Sensitive keys in stringified JSON/Dictionaries (NAME, EMAIL, MOBILE, etc.)
    """

    # Regex for typical PII
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[- ]?)?\d{10,}\b')
    
    # Sensitive keys to mask in key=value or "key": "value" patterns
    SENSITIVE_KEYS = [
        'NAME', 'LAST_NAME', 'SUR_NAME', 'PATIENT_NAME',
        'MOBILE', 'PHONE', 'EMAIL', 'PATIENT_MOBILE_NUMBER', 'PATIENT_EMAIL',
        'POC_MOBILE_NUMBER', 'POC_EMAIL', 'ADDRESS', 'ZIPCODE',
        'LICENSE_KEY', 'LICENSE_SECRET', 'PASSWORD'
    ]

    def filter(self, record):
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)
        
        record.msg = self.mask_pii(record.msg)
        return True

    def mask_pii(self, text):
        # 1. Mask Emails
        text = self.EMAIL_REGEX.sub('[REDACTED_EMAIL]', text)
        
        # 2. Mask Phone Numbers
        text = self.PHONE_REGEX.sub('[REDACTED_PHONE]', text)
        
        # 3. Mask Sensitive Keys (supports JSON and key=value)
        for key in self.SENSITIVE_KEYS:
            # Case insensitive match for key
            # Pattern for "key": "value" or 'key': 'value'
            json_pattern = re.compile(r'([\'"]' + key + r'[\'"]\s*:\s*)([\'"])(?:(?!\2).)*(\2)', re.IGNORECASE)
            text = json_pattern.sub(r'\1\2[REDACTED]\3', text)
            
            # Pattern for key=value
            kv_pattern = re.compile(r'(\b' + key + r'[\s]*=[\s]*)([^\s&,}]*)', re.IGNORECASE)
            text = kv_pattern.sub(r'\1[REDACTED]', text)

        return text

def mask_message(msg):
    """Utility function to manually mask a message."""
    filter_obj = PIIMaskingFilter()
    return filter_obj.mask_pii(str(msg))
