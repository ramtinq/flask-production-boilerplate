import time
import random
from models import CalculationResult
from app import db, create_app

from celery_app import celery

@celery.task
def random_number(max_value):
    print("\n----->Generating a random number...\n")
    time.sleep(15)
    return random.randint(0, max_value)


def estimate_pi(num_samples: int) -> float:

    print("\n----->calculating PI estimation...\n")

    random_float = random.random
    inside_circle = 0
    
    for _ in range(num_samples):
        x = random_float()
        y = random_float()

        if x * x + y * y <= 1.0:
            inside_circle += 1
            
    return 4.0 * inside_circle / num_samples


@celery.task
def compute_heavy_data(input_param):
    # Pure processing.
    return estimate_pi(input_param)

@celery.task
def store_result_to_db(computed_data, user_id: int):
    print("\n----->Storing to db...\n")
    # explicitly designed to handle the database persistence
    temp_app = create_app(is_worker=True)

    result = CalculationResult(data=computed_data, user_id=user_id)

    with temp_app.app_context():
        db.session.add(result)
        db.session.commit()
        return result.id
