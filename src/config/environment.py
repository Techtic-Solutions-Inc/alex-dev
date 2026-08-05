import os
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

    @classmethod
    def current(cls) -> "Environment":
        raw = os.getenv("ENVIRONMENT", "development").lower().strip()
        mapping = {
            "dev": cls.DEVELOPMENT,
            "development": cls.DEVELOPMENT,
            "staging": cls.STAGING,
            "stg": cls.STAGING,
            "production": cls.PRODUCTION,
            "prod": cls.PRODUCTION,
            "testing": cls.TESTING,
            "test": cls.TESTING,
        }
        return mapping.get(raw, cls.DEVELOPMENT)


def is_production() -> bool:
    return Environment.current() == Environment.PRODUCTION


def is_testing() -> bool:
    return Environment.current() == Environment.TESTING


def get_pool_size() -> int:
    explicit = os.getenv("DB_POOL_SIZE")
    if explicit:
        return int(explicit)
    env = Environment.current()
    return {
        Environment.DEVELOPMENT: 5,
        Environment.TESTING: 2,
        Environment.STAGING: 10,
        Environment.PRODUCTION: 20,
    }.get(env, 5)


def get_pool_max_overflow() -> int:
    explicit = os.getenv("DB_POOL_MAX_OVERFLOW")
    if explicit:
        return int(explicit)
    env = Environment.current()
    return {
        Environment.DEVELOPMENT: 5,
        Environment.TESTING: 0,
        Environment.STAGING: 10,
        Environment.PRODUCTION: 20,
    }.get(env, 5)
