from src.utils.security import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("Password1!")
    assert verify_password("Password1!", hashed) is True
    assert verify_password("wrong", hashed) is False
