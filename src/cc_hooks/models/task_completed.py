from typing import Literal

from pydantic import Field

from cc_hooks.models._base import BaseInput, BaseOutput


class TaskCompletedInput(BaseInput):
    hook_event_name: Literal["TaskCompleted"] = Field("TaskCompleted", alias="hookEventName")
    task_id: str = Field(alias="taskId")
    task_subject: str = Field(alias="taskSubject")
    task_description: str | None = Field(None, alias="taskDescription")
    teammate_name: str | None = Field(None, alias="teammateName")
    team_name: str | None = Field(None, alias="teamName")


class TaskCompletedOutput(BaseOutput):
    pass
