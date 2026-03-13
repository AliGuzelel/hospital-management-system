from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="Task Service")

tasks = []
task_id_counter = 1


class TaskRequest(BaseModel):
    title: str
    description: str


@app.get("/")
def root():
    return {"message": "Task Service is running"}


@app.post("/tasks")
def create_task(data: TaskRequest):
    global task_id_counter

    task = {
        "id": task_id_counter,
        "title": data.title,
        "description": data.description
    }

    tasks.append(task)
    task_id_counter += 1

    try:
        requests.post(
            "http://127.0.0.1:8003/notify",
            json={"message": f"Task created: {data.title}"}
        )
    except:
        pass

    return {"task": task}


@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: TaskRequest):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = data.title
            task["description"] = data.description

            try:
                requests.post(
                    "http://127.0.0.1:8003/notify",
                    json={"message": f"Task updated: {data.title}"}
                )
            except:
                pass

            return {"task": task}

    return {"error": "Task not found"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)

            try:
                requests.post(
                    "http://127.0.0.1:8003/notify",
                    json={"message": f"Task deleted: {task['title']}"}
                )
            except:
                pass

            return {"message": "Task deleted"}

    return {"error": "Task not found"}