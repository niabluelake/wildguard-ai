from werkzeug.security import check_password_hash, generate_password_hash

from services.db_service import execute, fetch_one


def get_user_by_username(username):
    sql = """
        SELECT
            user_id,
            username,
            password_hash,
            name,
            email,
            created_at
        FROM users
        WHERE username = :username
    """

    return fetch_one(sql, {"username": username})


def register_user(username, password, name=None, email=None):
    if get_user_by_username(username) is not None:
        raise ValueError("이미 사용 중인 아이디입니다.")

    sql = """
        INSERT INTO users (
            username,
            password_hash,
            name,
            email
        ) VALUES (
            :username,
            :password_hash,
            :name,
            :email
        )
    """

    params = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "name": name,
        "email": email,
    }

    return execute(sql, params)


def authenticate_user(username, password):
    user = get_user_by_username(username)

    if user is None:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    user.pop("password_hash", None)
    return user
