# -*- coding: utf-8 -*-

import web

from nailgun.api.models import Task
from nailgun.api.handlers.base import JSONHandler, content_json
from nailgun.jsonloader import json


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
        if user_data.cluster_id:
            tasks = self.db.query(Task).filter_by(
                cluster_id=user_data.cluster_id).all()
        else:
            tasks = self.db.query(Task).all()
        return map(
            TaskHandler.render,
            tasks
        )
