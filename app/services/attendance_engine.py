# from datetime import datetime, timedelta

# attendance_sessions = {}

# def start_attendance_session(class_id):

#     start_time = datetime.now()

#     end_time = start_time + timedelta(minutes=2)

#     attendance_sessions[class_id] = {
#         "start": start_time,
#         "end": end_time
#     }

#     return attendance_sessions[class_id]


# def is_attendance_open(class_id):

#     if class_id not in attendance_sessions:
#         return False

#     now = datetime.now()

#     session = attendance_sessions[class_id]

#     if session["start"] <= now <= session["end"]:
#         return True

#     return False


from datetime import datetime, timedelta

# In-memory store for active sessions
attendance_sessions = {}

def start_attendance_session(class_id, duration_minutes=60):
    """
    Starts a session. Defaulting to 60 minutes to match your service logic.
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)

    attendance_sessions[class_id] = {
        "start": start_time,
        "end": end_time,
        "active": True
    }

    return attendance_sessions[class_id]

def is_attendance_open(class_id):
    """
    Checks if the specific session is still within the valid time window.
    """
    if class_id not in attendance_sessions:
        return False

    session = attendance_sessions[class_id]
    now = datetime.now()

    # Verify time window
    if session["start"] <= now <= session["end"] and session.get("active"):
        return True
        
    return False

def close_attendance_session(class_id):
    """
    Manually close a session if the teacher ends it early.
    """
    if class_id in attendance_sessions:
        attendance_sessions[class_id]["active"] = False
        return True
    return False