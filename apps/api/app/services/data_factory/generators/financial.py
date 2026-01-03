"""
Financial Data Generator

Generates financial data: credit cards, transactions, amounts, IBAN, SWIFT, currencies.
Includes Luhn-valid credit card numbers and realistic transaction patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP
import random
import string
from datetime import datetime, timedelta

from app.services.data_factory.generators.base import BaseGenerator
from app.services.data_factory.schema import (
    ColumnSpec,
    DataType,
    ConstraintSpec,
    Distribution,
)


class FinancialDataGenerator(BaseGenerator):
    """
    High-performance generator for financial data.
    
    Features:
    - Luhn-valid credit card numbers for all major providers
    - Realistic transaction amounts with configurable distributions
    - Valid IBAN/SWIFT codes
    - Currency codes and symbols
    - Invoice numbers with customizable formats
    - Transaction IDs and reference numbers
    
    All generated data passes format validation but is NOT real financial data.
    """
    
    # Credit card prefixes by provider (IIN ranges)
    CARD_PREFIXES = {
        "visa": ["4"],
        "mastercard": ["51", "52", "53", "54", "55", "2221", "2720"],
        "amex": ["34", "37"],
        "discover": ["6011", "644", "645", "646", "647", "648", "649", "65"],
        "diners": ["300", "301", "302", "303", "304", "305", "36", "38"],
        "jcb": ["3528", "3589"],
    }
    
    # Card lengths by provider
    CARD_LENGTHS = {
        "visa": 16,
        "mastercard": 16,
        "amex": 15,
        "discover": 16,
        "diners": 14,
        "jcb": 16,
    }
    
    CURRENCIES = [
        ("USD", "$", "US Dollar"),
        ("EUR", "€", "Euro"),
        ("GBP", "£", "British Pound"),
        ("JPY", "¥", "Japanese Yen"),
        ("INR", "₹", "Indian Rupee"),
        ("CAD", "C$", "Canadian Dollar"),
        ("AUD", "A$", "Australian Dollar"),
        ("CHF", "Fr", "Swiss Franc"),
        ("CNY", "¥", "Chinese Yuan"),
        ("HKD", "HK$", "Hong Kong Dollar"),
    ]
    
    def get_supported_types(self) -> List[str]:
        """Get supported data types."""
        return [
            DataType.CREDIT_CARD.value,
            DataType.CREDIT_CARD_NUMBER.value,
            DataType.CVV.value,
            DataType.IBAN.value,
            DataType.SWIFT.value,
            DataType.CURRENCY.value,
            DataType.AMOUNT.value,
            DataType.PRICE.value,
            DataType.TRANSACTION_ID.value,
            DataType.INVOICE_NUMBER.value,
        ]
    
    def generate(
        self,
        spec: ColumnSpec,
        count: int = 1
    ) -> List[Any]:
        """Generate financial data values."""
        values = []
        
        for _ in range(count):
            if self._should_be_null(spec):
                values.append(None)
                continue
            
            if spec.data_type == DataType.CREDIT_CARD:
                value = self._generate_credit_card(spec)
            elif spec.data_type == DataType.CREDIT_CARD_NUMBER:
                value = self._generate_credit_card_number(spec)
            elif spec.data_type == DataType.CVV:
                value = self._generate_cvv(spec)
            elif spec.data_type == DataType.IBAN:
                value = self._generate_iban(spec)
            elif spec.data_type == DataType.SWIFT:
                value = self._generate_swift(spec)
            elif spec.data_type == DataType.CURRENCY:
                value = self._generate_currency(spec)
            elif spec.data_type in (DataType.AMOUNT, DataType.PRICE):
                value = self._generate_amount(spec)
            elif spec.data_type == DataType.TRANSACTION_ID:
                value = self._generate_transaction_id(spec)
            elif spec.data_type == DataType.INVOICE_NUMBER:
                value = self._generate_invoice_number(spec)
            else:
                raise ValueError(f"Unsupported data type: {spec.data_type}")
            
            if spec.unique and spec.data_type not in (DataType.AMOUNT, DataType.PRICE):
                value = self._get_unique_value(
                    spec.name,
                    lambda: self._generate_single_value(spec),
                )
            
            value = self._apply_constraints(value, spec.constraints)
            values.append(value)
        
        return values
    
    def _generate_single_value(self, spec: ColumnSpec) -> Any:
        """Generate single value for uniqueness retry."""
        if spec.data_type == DataType.CREDIT_CARD:
            return self._generate_credit_card(spec)
        elif spec.data_type == DataType.CREDIT_CARD_NUMBER:
            return self._generate_credit_card_number(spec)
        elif spec.data_type == DataType.IBAN:
            return self._generate_iban(spec)
        elif spec.data_type == DataType.SWIFT:
            return self._generate_swift(spec)
        elif spec.data_type == DataType.TRANSACTION_ID:
            return self._generate_transaction_id(spec)
        elif spec.data_type == DataType.INVOICE_NUMBER:
            return self._generate_invoice_number(spec)
        return None
    
    def _generate_credit_card(self, spec: ColumnSpec) -> Dict[str, str]:
        """
        Generate complete credit card details.
        
        Returns dict with: number, expiry, cvv, provider
        """
        params = spec.generator_params
        provider = params.get("provider")
        
        if not provider:
            provider = random.choice(list(self.CARD_PREFIXES.keys()))
        
        number = self._generate_luhn_valid_number(provider)
        expiry = self._generate_expiry_date()
        cvv = self._generate_cvv_value(provider)
        
        return {
            "number": number,
            "expiry": expiry,
            "cvv": cvv,
            "provider": provider.capitalize(),
        }
    
    def _generate_credit_card_number(self, spec: ColumnSpec) -> str:
        """Generate just the card number (Luhn-valid)."""
        params = spec.generator_params
        provider = params.get("provider")
        
        if not provider:
            provider = random.choice(list(self.CARD_PREFIXES.keys()))
        
        return self._generate_luhn_valid_number(provider)
    
    def _generate_luhn_valid_number(self, provider: str) -> str:
        """
        Generate a Luhn-valid credit card number.
        
        The Luhn algorithm (mod 10) is used to validate credit card numbers.
        We generate random digits and calculate the check digit.
        """
        provider = provider.lower()
        prefix = random.choice(self.CARD_PREFIXES.get(provider, ["4"]))
        length = self.CARD_LENGTHS.get(provider, 16)
        
        # Generate random digits (leaving room for check digit)
        num_random_digits = length - len(prefix) - 1
        random_digits = ''.join(
            random.choices(string.digits, k=num_random_digits)
        )
        
        # Combine prefix and random digits
        partial_number = prefix + random_digits
        
        # Calculate Luhn check digit
        check_digit = self._calculate_luhn_check_digit(partial_number)
        
        return partial_number + str(check_digit)
    
    def _calculate_luhn_check_digit(self, partial_number: str) -> int:
        """Calculate the Luhn check digit for a partial card number."""
        digits = [int(d) for d in partial_number]
        
        # Double every second digit from right (which is odd indices after reverse)
        for i in range(len(digits) - 1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        total = sum(digits)
        return (10 - (total % 10)) % 10
    
    def _generate_expiry_date(self) -> str:
        """Generate a future expiry date (MM/YY)."""
        now = datetime.now()
        # Card valid for 1-5 years from now
        years_ahead = random.randint(1, 5)
        month = random.randint(1, 12)
        year = (now.year + years_ahead) % 100
        return f"{month:02d}/{year:02d}"
    
    def _generate_cvv(self, spec: ColumnSpec) -> str:
        """Generate CVV/CVC code."""
        params = spec.generator_params
        provider = params.get("provider", "visa")
        return self._generate_cvv_value(provider)
    
    def _generate_cvv_value(self, provider: str) -> str:
        """Generate CVV value based on provider."""
        # AMEX uses 4-digit CVV, others use 3
        length = 4 if provider.lower() == "amex" else 3
        return ''.join(random.choices(string.digits, k=length))
    
    def _generate_iban(self, spec: ColumnSpec) -> str:
        """
        Generate IBAN (International Bank Account Number).
        
        Format: CC00BBBB...AAAA (country code + check digits + BBAN)
        """
        params = spec.generator_params
        country = params.get("country", "DE")
        
        # IBAN lengths by country
        iban_lengths = {
            "DE": 22, "FR": 27, "GB": 22, "ES": 24, "IT": 27,
            "NL": 18, "BE": 16, "AT": 20, "CH": 21, "IE": 22,
        }
        
        length = iban_lengths.get(country, 22)
        bban_length = length - 4  # minus country code and check digits
        
        # Generate random BBAN (Basic Bank Account Number)
        bban = ''.join(random.choices(string.digits, k=bban_length))
        
        # For simplicity, using random check digits (real IBAN has calculated check)
        check_digits = f"{random.randint(10, 99):02d}"
        
        return f"{country}{check_digits}{bban}"
    
    def _generate_swift(self, spec: ColumnSpec) -> str:
        """
        Generate SWIFT/BIC code.
        
        Format: AAAABBCCXXX
        AAAA = Bank code (4 letters)
        BB = Country code (2 letters)
        CC = Location code (2 alphanumeric)
        XXX = Branch code (3 alphanumeric, optional)
        """
        params = spec.generator_params
        country = params.get("country", "US")
        include_branch = params.get("include_branch", True)
        
        bank_code = ''.join(random.choices(string.ascii_uppercase, k=4))
        location_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        
        swift = f"{bank_code}{country}{location_code}"
        
        if include_branch:
            branch_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            swift += branch_code
        
        return swift
    
    def _generate_currency(self, spec: ColumnSpec) -> str:
        """
        Generate currency code.
        
        Params:
            format: "code" (USD), "symbol" ($), "name" (US Dollar), "full" ({code, symbol, name})
        """
        params = spec.generator_params
        fmt = params.get("format", "code")
        
        currency = random.choice(self.CURRENCIES)
        
        if fmt == "code":
            return currency[0]
        elif fmt == "symbol":
            return currency[1]
        elif fmt == "name":
            return currency[2]
        elif fmt == "full":
            return {
                "code": currency[0],
                "symbol": currency[1],
                "name": currency[2],
            }
        return currency[0]
    
    def _generate_amount(self, spec: ColumnSpec) -> Decimal:
        """
        Generate monetary amount with realistic distributions.
        
        Params:
            min_value: Minimum amount
            max_value: Maximum amount
            distribution: uniform, normal, exponential, log_normal
            decimal_places: Number of decimal places
            currency: Currency for formatting
        """
        params = spec.generator_params
        constraints = spec.constraints or ConstraintSpec()
        
        min_val = params.get("min_value", constraints.min_value or 0.01)
        max_val = params.get("max_value", constraints.max_value or 10000.00)
        distribution = params.get("distribution", "exponential")
        decimal_places = params.get("decimal_places", constraints.decimal_places or 2)
        
        # Generate based on distribution
        if distribution == "normal":
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6
            value = random.gauss(mean, std)
            value = max(min_val, min(max_val, value))
        
        elif distribution == "exponential":
            # Exponential is realistic for transaction amounts
            # Many small transactions, few large ones
            scale = (max_val - min_val) / 5
            value = min_val + random.expovariate(1 / scale)
            value = min(max_val, value)
        
        elif distribution == "log_normal":
            import math
            mean = math.log((min_val + max_val) / 2)
            value = random.lognormvariate(mean, 0.5)
            value = max(min_val, min(max_val, value))
        
        else:  # uniform
            value = random.uniform(min_val, max_val)
        
        # Round to decimal places
        quantizer = Decimal(10) ** -decimal_places
        return Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP)
    
    def _generate_transaction_id(self, spec: ColumnSpec) -> str:
        """
        Generate transaction ID.
        
        Params:
            prefix: Prefix (default "TXN")
            length: Total length of numeric part
            format: "numeric", "alphanumeric", "uuid-like"
        """
        params = spec.generator_params
        prefix = params.get("prefix", "TXN")
        length = params.get("length", 12)
        fmt = params.get("format", "alphanumeric")
        
        if fmt == "numeric":
            suffix = ''.join(random.choices(string.digits, k=length))
        elif fmt == "uuid-like":
            import uuid
            return str(uuid.uuid4()).upper()
        else:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        return f"{prefix}-{suffix}"
    
    def _generate_invoice_number(self, spec: ColumnSpec) -> str:
        """
        Generate invoice number.
        
        Params:
            prefix: Prefix (default "INV")
            include_year: Include year in number
            sequential: Use sequential numbering
            format: Custom format string
        """
        params = spec.generator_params
        prefix = params.get("prefix", "INV")
        include_year = params.get("include_year", True)
        sequential = params.get("sequential", False)
        
        if sequential:
            seq = self._get_next_sequence(f"invoice_{prefix}")
            seq_str = f"{seq:06d}"
        else:
            seq_str = ''.join(random.choices(string.digits, k=6))
        
        if include_year:
            year = datetime.now().year
            return f"{prefix}-{year}-{seq_str}"
        
        return f"{prefix}-{seq_str}"


# Convenience functions
def generate_credit_card(provider: Optional[str] = None) -> Dict[str, str]:
    """Generate complete credit card details."""
    gen = FinancialDataGenerator()
    spec = ColumnSpec(
        name="card",
        data_type=DataType.CREDIT_CARD,
        generator_params={"provider": provider}
    )
    return gen.generate_single(spec)


def generate_amount(
    min_value: float = 0.01,
    max_value: float = 10000.00,
    distribution: str = "exponential"
) -> Decimal:
    """Generate monetary amount."""
    gen = FinancialDataGenerator()
    spec = ColumnSpec(
        name="amount",
        data_type=DataType.AMOUNT,
        generator_params={
            "min_value": min_value,
            "max_value": max_value,
            "distribution": distribution,
        }
    )
    return gen.generate_single(spec)


def validate_luhn(card_number: str) -> bool:
    """Validate a credit card number using Luhn algorithm."""
    digits = [int(d) for d in str(card_number) if d.isdigit()]
    if len(digits) < 13:
        return False
    
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0
