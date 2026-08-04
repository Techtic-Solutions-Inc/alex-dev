import pytest

from utils.password import hash_password, validate_password_strength, verify_password


def test_validate_password_strength_accepts_strong_password() -> None:
    validate_password_strength("StrongPass1!")


@pytest.mark.parametrize(
    "password",
    [
        "short1!",
        "alllowercase1!",
        "ALLUPPERCASE1!",
        "NoDigitsHere!",
        "NoSpecialChar1",
    ],
)
def test_validate_password_strength_rejects_weak_password(password: str) -> None:
    with pytest.raises(ValueError, match="Password must contain"):
        validate_password_strength(password)


def test_validate_password_too_short_mentions_length() -> None:
    with pytest.raises(ValueError, match="at least 8 characters"):
        validate_password_strength("Aa1!")


def test_validate_password_missing_uppercase_mentions_uppercase() -> None:
    with pytest.raises(ValueError, match="uppercase"):
        validate_password_strength("lowercase1!")


def test_validate_password_missing_lowercase_mentions_lowercase() -> None:
    with pytest.raises(ValueError, match="lowercase"):
        validate_password_strength("UPPERCASE1!")


def test_validate_password_missing_digit_mentions_digit() -> None:
    with pytest.raises(ValueError, match="digit"):
        validate_password_strength("NoDigitHere!")


def test_validate_password_missing_special_mentions_special() -> None:
    with pytest.raises(ValueError, match="special"):
        validate_password_strength("NoSpecialChar1")


def test_validate_password_multiple_failures() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("abc")
    detail = str(exc_info.value)
    assert "at least 8 characters" in detail
    assert "uppercase" in detail
    assert "digit" in detail
    assert "special" in detail


def test_hash_and_verify_password() -> None:
    hashed = hash_password("StrongPass1!")
    assert verify_password("StrongPass1!", hashed)
    assert not verify_password("WrongPass1!", hashed)


def test_hash_password_produces_unique_hashes() -> None:
    hash1 = hash_password("StrongPass1!")
    hash2 = hash_password("StrongPass1!")
    assert hash1 != hash2
    assert verify_password("StrongPass1!", hash1)
    assert verify_password("StrongPass1!", hash2)
