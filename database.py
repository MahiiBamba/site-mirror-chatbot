import sqlite3

DB_NAME = "chat_history.db"


def get_connection():
    return sqlite3.connect(DB_NAME)



def create_conversation():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations DEFAULT VALUES
    """)

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


def save_message(conversation_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    """, (conversation_id, role, content))

    conn.commit()
    conn.close()
    print("MESSAGE SAVED:", conversation_id, role, content)



def get_conversation_history(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC, id ASC
    """, (conversation_id,))

    messages = cursor.fetchall()

    conn.close()

    return messages


def format_conversation_history(conversation_id):
    history = get_conversation_history(conversation_id)

    if not history:
        return ""

    formatted_history = []

    for role, content in history:
        if role == "user":
            formatted_history.append(f"User: {content}")
        elif role == "assistant":
            formatted_history.append(f"Assistant: {content}")

    return "\n".join(formatted_history)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
            REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()

    conversation_id = create_conversation()

    save_message(
        conversation_id,
        "user",
        "What services do you provide?"
    )

    save_message(
        conversation_id,
        "assistant",
        "We provide web development services."
    )

    history = get_conversation_history(conversation_id)

    print("Conversation ID:", conversation_id)
    print("History:")

    for role, content in history:
        print(role, ":", content)

