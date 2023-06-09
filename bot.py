import base64
import os
import random
import sys
from datetime import datetime
from typing import List

import psycopg2
from dotenv import load_dotenv
from faker import Faker

from apps.utils import constants  # noqa

load_dotenv()
fake = Faker()


def handle_cursor_result(cursor_result):
    return cursor_result if cursor_result is not None else 0


def get_encoded(word):
    sample_string_bytes = word.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")

    return base64_string


def number_of_users():
    cursor = get_cursor()

    cursor.execute("SELECT COUNT(*) FROM users_customuser;")

    return handle_cursor_result(cursor.fetchone()[0])


def get_last_user_id():
    cursor = get_cursor()

    cursor.execute("SELECT MAX(id) FROM users_customuser;")

    return handle_cursor_result(cursor.fetchone()[0])


def get_last_like_id():
    cursor = get_cursor()

    cursor.execute("SELECT MAX(id) FROM posts_like")

    return handle_cursor_result(cursor.fetchone()[0])


def number_of_posts():
    cursor = get_cursor()

    cursor.execute("SELECT COUNT(*) FROM posts_post")

    return handle_cursor_result(cursor.fetchone()[0])


def get_last_post_id():
    cursor = get_cursor()

    cursor.execute("SELECT MAX(id) FROM posts_post")

    return handle_cursor_result(cursor.fetchone()[0])


def max_posts_per_user():
    return constants.MAX_POST_PER_USER


def max_likes_per_user():
    return constants.MAX_LIKE_PER_USER


def create_users(user_amount):
    fake_date = "2023-03-22 07:54:07.474753"
    last_user_id = get_last_user_id()
    user_data = [
        (
            last_user_id + i + 1,
            get_encoded(fake.name()),
            fake_date,
            False,
            fake.name(),
            "",
            "",
            fake.email(),
            False,
            True,
            fake_date,
            fake_date,
        )
        for i in range(user_amount)
    ]

    cursor = get_cursor()

    cursor.executemany(
        "INSERT INTO users_customuser (id, password, last_login, is_superuser, "
        "username, first_name, last_name, email, is_staff, is_active, date_joined, "
        "last_activity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        user_data,
    )

    cursor.connection.commit()


def create_likes_and_dislikes_for_new_posts(
    last_post_id, new_last_post_id, last_user_id, new_last_user_id
):
    likes = []
    dislikes = []
    last_like_id = get_last_like_id()
    cursor = get_cursor()

    like_count = 0
    current_time = str(datetime.now())
    for user_id in range(last_user_id, new_last_user_id):
        for post_id in range(last_post_id, new_last_post_id):
            for i in range(0, random.randint(0, constants.MAX_LIKE_PER_USER)):
                like_count += 1
                likes.append(
                    (last_like_id + like_count, current_time, "LIKE", user_id, post_id)
                )
            for i in range(0, random.randint(0, constants.MAX_DISLIKE_PER_USER)):
                like_count += 1
                dislikes.append(
                    (
                        last_like_id + like_count,
                        current_time,
                        "DISLIKE",
                        user_id,
                        post_id,
                    )
                )

    data = likes + dislikes

    cursor.executemany(
        "INSERT INTO posts_like (id, created, like_type, author_id, post_id) VALUES (%s, %s, %s, %s, %s)",
        data,
    )

    cursor.connection.commit()


def create_posts_for_new_users(last_user_id, new_last_user_id):
    cursor = get_cursor()

    last_post_id = get_last_post_id()
    counter = 0
    post_data = []

    for author_id in range(last_user_id, new_last_user_id + 1):
        for j in range(random.randint(0, constants.MAX_POST_PER_USER)):
            counter += 1
            post_data.append(
                (last_post_id + counter, fake.name(), fake.name(), author_id)
            )

    cursor.executemany(
        "INSERT INTO posts_post (id, title, text, author_id) VALUES (%s, %s, %s, %s)",
        post_data,
    )
    cursor.connection.commit()
    new_last_post_id = get_last_post_id()
    create_likes_and_dislikes_for_new_posts(
        last_post_id, new_last_post_id, last_user_id, new_last_user_id
    )


def signup_users(parameters: List[str]):
    user_amount = int(parameters[2])

    last_user_id = get_last_user_id()
    create_users(user_amount)
    new_last_user_id = get_last_user_id()

    create_posts_for_new_users(last_user_id, new_last_user_id)

    return f"Successfully created {user_amount} users"


config_methods = {
    "number_of_users": number_of_users,
    "number_of_posts": number_of_posts,
    "max_posts_per_user": max_posts_per_user,
    "max_likes_per_user": max_likes_per_user,
    "signup_users": signup_users,
}


def get_cursor():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
    except Exception as e:
        raise Exception(str(e))

    return connection.cursor()


def main():
    config = sys.argv[1]
    if config_methods.get(config):
        if len(sys.argv) > 2:
            print(config_methods[config](parameters=sys.argv))
        else:
            print(config_methods[config]())
    else:
        print(f"{config} command is not found")


if __name__ == "__main__":
    main()
