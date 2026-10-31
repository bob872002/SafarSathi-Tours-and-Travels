
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "safarsathi_db"),
    )


if __name__ == "__main__":
    try:
        connection = get_connection()
        print("SafarSathi database connected successfully!")
        connection.close()
    except mysql.connector.Error as error:
        print("Database connection failed:", error)
