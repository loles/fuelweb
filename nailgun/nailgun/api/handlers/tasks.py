# -*- coding: utf-8 -*-

import json

import web

from nailgun.api.models import Task
from nailgun.api.handlers.base import JSONHandler, content_json


class TaskHandler(JSONHandler):
    fields = (
        "id",
        "cluster",
        "uuid",
        "name",
        "result",
        "message",
        "status",
        "progress"
    )
    model = Task

    @content_json
    def GET(self, task_id):
        task = self.get_object_or_404(Task, task_id)
        return self.render(task)

    def DELETE(self, task_id):
        task = self.get_object_or_404(Task, task_id)
        if task.status not in ("ready", "error"):
            raise web.badrequest("You cannot delete running task manually")
        for subtask in task.subtasks:
            self.db.delete(subtask)
        self.db.delete(task)
        self.db.commit()
        raise web.webapi.HTTPError(
            status="204 No Content",
            data=""
        )


class TaskCollectionHandler(JSONHandler):

    @content_json
    def GET(self):
        user_data = web.input(cluster_id=None)
        tasks_query = self.db.query(Task)
        if user_data.cluster_id:
            tasks_query = tasks_query.filter_by(
                cluster_id=user_data.cluster_id)
        tasks = self.fetch_collection(tasks_query)
        return map(
            TaskHandler.render,
            tasks
        )
