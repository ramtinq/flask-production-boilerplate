from flask import jsonify
from . import calculations_bp

from app.celery_app import celery
from celery.result import AsyncResult
from .tasks import random_number

@calculations_bp.get("/task/generate-random/<int:maximum>")
def start_task(maximum):
    result = random_number.delay(maximum)

    return jsonify({
        "task_id": result.id,
        "state": result.state
    })


@calculations_bp.get("/task/result/<task_id>")
def get_task(task_id):
    result = AsyncResult(task_id, app=celery)

    if result.ready():
        return jsonify({
            "state": result.state,
            "result": result.get()
        })

    return jsonify({
        "state": result.state
    })