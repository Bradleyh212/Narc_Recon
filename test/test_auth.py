import pytest 

from src.auth import _hash_secret, _verify_secret

def test_password_hash_and_verify():
	pwd = "123"
	hashv = _hash_secret(pwd)
	assert _verify_secret(hashv, pwd) == True
	assert _verify_secret(hashv, "idk") == False
	assert _verify_secret(hashv, "12") == False # Testing edge cases
	assert _verify_secret(hashv, "1234") == False # Testing edge cases





