# Timezone padrao do app (deploy EasyPanel / Brasil = UTC-3)
# Sempre use America/Sao_Paulo — nao depender do fuso do SO do container.

from datetime import date, datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE

TZ = ZoneInfo(TIMEZONE)


def agora_sp() -> datetime:
    return datetime.now(TZ)


def hoje_sp() -> date:
    return agora_sp().date()


def ano_atual_sp() -> int:
    return agora_sp().year
