from src.tools.login.password import hash_password, verify_password


def test_verify_password_accepts_the_original_password():
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", password_hash)


def test_verify_password_rejects_a_different_password():
    password_hash = hash_password("correct horse battery staple")

    assert not verify_password("wrong password", password_hash)
