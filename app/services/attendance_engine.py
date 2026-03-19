from datetime import datetime, timedelta

attendance_sessions = {}

def start_attendance_session(class_id):

    start_time = datetime.now()

    end_time = start_time + timedelta(minutes=2)

    attendance_sessions[class_id] = {
        "start": start_time,
        "end": end_time
    }

    return attendance_sessions[class_id]


def is_attendance_open(class_id):

    if class_id not in attendance_sessions:
        return False

    now = datetime.now()

    session = attendance_sessions[class_id]

    if session["start"] <= now <= session["end"]:
        return True

    return False