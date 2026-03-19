from datetime import datetime

def current_time():


  return datetime.now().time()


def current_day():

  return datetime.now().strftime("%A")

