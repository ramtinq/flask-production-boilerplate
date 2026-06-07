import time
import random

from app.celery_app import celery

@celery.task(name="calculations.random_number")
def random_number(max_value):
    print("\n----->Generating a random number...\n")
    time.sleep(15)
    return random.randint(0, max_value)
