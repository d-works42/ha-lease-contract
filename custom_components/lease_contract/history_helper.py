"""Best-effort lookup of a past odometer reading via the recorder.

This is only ever used as a *fallback* to reduce drift when Home Assistant
was restarted around a month boundary. It relies on the recorder having
kept history far enough back, which depends on the user's own
`recorder: purge_keep_days` setting (default 10 days) - it is not a
substitute for an accurate manual baseline.
"""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_get_historical_odometer(
    hass: HomeAssistant, entity_id: str, point_in_time: datetime
) -> float | None:
    """Return the entity's numeric state at/just before point_in_time, or None."""
    try:
        from homeassistant.components.recorder import get_instance, history
    except ImportError:
        return None

    try:
        instance = get_instance(hass)
    except (KeyError, RuntimeError):
        # Recorder not set up / not ready.
        return None

    def _fetch() -> float | None:
        try:
            states = history.get_states(hass, point_in_time, entity_ids=[entity_id])
        except Exception:  # pragma: no cover - defensive, recorder API varies by HA version
            _LOGGER.debug("Recorder history lookup failed for %s", entity_id, exc_info=True)
            return None
        if not states:
            return None
        try:
            return float(states[0].state)
        except (ValueError, TypeError):
            return None

    return await instance.async_add_executor_job(_fetch)
