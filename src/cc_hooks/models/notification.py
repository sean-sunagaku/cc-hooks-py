from typing import Literal

from pydantic import Field

from cc_hooks.enums import NotificationType
from cc_hooks.models._base import BaseInput, BaseOutput


class NotificationInput(BaseInput):
    hook_event_name: Literal["Notification"] = Field("Notification", alias="hookEventName")
    message: str
    title: str | None = None
    notification_type: str = Field(alias="notificationType")

    def as_known_notification_type(self) -> NotificationType | None:
        try:
            return NotificationType(self.notification_type)
        except ValueError:
            return None


class NotificationOutput(BaseOutput):
    pass
