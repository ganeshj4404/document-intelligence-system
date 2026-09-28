import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/document_intelligence.db")


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """
    Create the documents table if it does not already exist.
    """

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            status TEXT NOT NULL,
            validation_status TEXT,
            summary_validation_status TEXT,
            summary_path TEXT,
            summary_audio_path TEXT,
            paraphrase_path TEXT,
            audio_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            processed_at TEXT
        )
        """
    )

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

    add_summary_audio_column()


def create_document(
    file_name,
    file_path,
    status="uploaded"
):
    """
    Insert a new document into the database.
    """

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO documents (
            file_name,
            file_path,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            file_name,
            str(file_path),
            status
        )
    )

    connection.commit()

    document_id = cursor.lastrowid

    connection.close()

    return document_id


def update_document(
    document_id,
    status=None,
    validation_status=None,
    summary_validation_status=None,
    summary_path=None,
    summary_audio_path=None,
    paraphrase_path=None,
    audio_path=None
):
    """
    Update information about a processed document.
    """

    connection = get_connection()

    connection.execute(
        """
        UPDATE documents
        SET
            status = COALESCE(?, status),
            validation_status = COALESCE(?, validation_status),
            summary_validation_status = COALESCE(?, summary_validation_status),
            summary_path = COALESCE(?, summary_path),
            summary_audio_path = ?,
            paraphrase_path = COALESCE(?, paraphrase_path),
            audio_path = COALESCE(?, audio_path),
            processed_at = CASE
                WHEN ? = 'completed' OR ? = 'failed'
                THEN CURRENT_TIMESTAMP
                ELSE processed_at
            END
        WHERE id = ?
        """,
        (
            status,
            validation_status,
            summary_validation_status,
            summary_path,
            summary_audio_path,
            paraphrase_path,
            audio_path,
            status,
            status,
            document_id
        )
    )

    connection.commit()
    connection.close()


def get_all_documents():
    """
    Return all documents from the database.
    """

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM documents
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def get_document_by_id(document_id):
    """
    Return one document by its ID.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM documents
        WHERE id = ?
        """,
        (document_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)

def delete_document(document_id):
    """
    Delete one document from the database.
    """

    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM documents
        WHERE id = ?
        """,
        (document_id,)
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted

def create_user(username, password_hash):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """,
        (username, password_hash)
    )

    connection.commit()
    user_id = cursor.lastrowid
    connection.close()

    return user_id


def get_user_by_username(username):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT * FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None

def add_summary_audio_column():
    connection = get_connection()

    columns = connection.execute(
        "PRAGMA table_info(documents)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "summary_audio_path" not in column_names:
        connection.execute(
            "ALTER TABLE documents ADD COLUMN summary_audio_path TEXT"
        )
        connection.commit()

    connection.close()