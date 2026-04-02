import enum


class AccountStatus(str, enum.Enum):
    NEW = "new"
    CODE_SENT = "code_sent"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
