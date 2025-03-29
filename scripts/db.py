from tinydb import TinyDB, Query

db = TinyDB("data.json")
table = db.table("users")


def user_has_application(user_id: int, application: str) -> bool:
    """Check if the user already has the specified application."""
    User = Query()
    return table.contains((User.user_id == user_id) & (User.application == application))


def add_user(user_id: int, application: str):
    """Add a user with an application, ensuring no duplicate applications per user."""
    if user_has_application(user_id, application):
        print(f"User {user_id} already has {application}.")
        return False  # Prevent duplicate application entries
    table.insert({"user_id": user_id, "application": application})
    return True


def get_user_applications(user_id: int):
    """Retrieve all applications associated with a user."""
    User = Query()
    return table.search(User.user_id == user_id)


def get_all_users():
    """Retrieve all user records."""
    return table.all()


def remove_user_application(user_id: int, application: str):
    """Remove a specific application for a user."""
    User = Query()
    table.remove((User.user_id == user_id) & (User.application == application))
