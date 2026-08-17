from pymongo.errors import DuplicateKeyError

class UserRepository:
    def create_user(self, user_data):
        try:
            # Insert user logic here
            pass
        except DuplicateKeyError as exc:
            if 'uq_users_email' in str(exc):
                return None
            raise
