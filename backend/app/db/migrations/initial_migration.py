from pymongo import ASCENDING, IndexModel

# Create a sparse index on username to avoid unique constraint on null values
username_index = IndexModel([('username', ASCENDING)], unique=True, sparse=True, name='uq_users_username')

# Migration logic here
