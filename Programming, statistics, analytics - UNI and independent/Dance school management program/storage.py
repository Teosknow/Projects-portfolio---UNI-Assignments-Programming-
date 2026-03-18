import pickle
import os
from school_manager import SchoolManager
from person import Person

DATA_FILE = "school_data.pkl"
TMP_FILE = DATA_FILE + ".tmp"


def save_manager(manager: SchoolManager) -> None:
    """Atomically save the entire SchoolManager object to a file."""
    # write to temp then atomically replace to avoid partial writes

    with open(TMP_FILE, "wb") as f:

        pickle.dump(manager, f)

    os.replace(TMP_FILE, DATA_FILE)

    print("Data saved successfully.")


def load_manager() -> SchoolManager:
    """Load SchoolManager from file, or create a new one if file doesn't exist."""

    if os.path.exists(DATA_FILE):

        try:

            with open(DATA_FILE, "rb") as f:
                manager = pickle.load(f)

            # --------------------------
            # Restore Person IDs
            # --------------------------
            max_id = -1

            for s in getattr(manager, "students", []):

                if hasattr(s, "id") and s.id is not None:
                    max_id = max(max_id, int(s.id))

            for t in getattr(manager, "teachers", []):

                if hasattr(t, "id") and t.id is not None:
                    max_id = max(max_id, int(t.id))

            Person._id_counter = max_id + 1

            # --------------------------
            # Restore Course IDs
            # --------------------------
            max_course_id = -1

            for c in getattr(manager, "courses", []):

                if hasattr(c, "id") and c.id is not None:
                    max_course_id = max(max_course_id, int(c.id))

            if max_course_id >= 0:
                from course import Course

                Course.set_id_counter(max_course_id + 1)

            print("Data loaded successfully.")
            return manager

        except Exception as e:
            print(f"Failed to load saved data ({e}). Creating a new manager.")

    return SchoolManager()
