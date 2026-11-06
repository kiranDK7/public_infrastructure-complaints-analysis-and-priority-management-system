from models.database import query_db, execute_db

class NotificationModel:
    @staticmethod
    def get_user_notifications(user_id, limit=20):
        return query_db(
            """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        )

    @staticmethod
    def get_unread_count(user_id):
        row = query_db(
            "SELECT COUNT(*) as c FROM notifications WHERE user_id = ? AND is_read = 0",
            (user_id,),
            one=True
        )
        return row['c'] if row else 0

    @staticmethod
    def mark_all_read(user_id):
        return execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))

