import hashlib
import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_cpf(cpf: str) -> str:
    digits = "".join(filter(str.isdigit, cpf))
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"


def validate_cpf(cpf: str) -> bool:
    digits = "".join(filter(str.isdigit, cpf))
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    for i in range(9, 11):
        val = sum(int(digits[j]) * (i + 1 - j) for j in range(i))
        dig = (val * 10 % 11) % 10
        if int(digits[i]) != dig:
            return False
    return True
