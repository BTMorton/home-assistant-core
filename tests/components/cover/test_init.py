"""The tests for Cover."""
from enum import Enum

import pytest

import homeassistant.components.cover as cover
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_PLATFORM,
    SERVICE_TOGGLE,
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import help_test_all, import_and_test_deprecated_constant_enum


async def test_services(hass: HomeAssistant, enable_custom_integrations: None) -> None:
    """Test the provided services."""
    platform = getattr(hass.components, "test.cover")

    platform.init()
    assert await async_setup_component(
        hass, cover.DOMAIN, {cover.DOMAIN: {CONF_PLATFORM: "test"}}
    )
    await hass.async_block_till_done()

    # ent1 = cover without tilt and position
    # ent2 = cover with position but no tilt
    # ent3 = cover with simple tilt functions and no position
    # ent4 = cover with all tilt functions but no position
    # ent5 = cover with all functions
    ent1, ent2, ent3, ent4, ent5 = platform.ENTITIES

    # Test init all covers should be open
    assert is_open(hass, ent1)
    assert is_open(hass, ent2)
    assert is_open(hass, ent3)
    assert is_open(hass, ent4)
    assert is_open(hass, ent5)

    # call basic toggle services
    await call_service(hass, SERVICE_TOGGLE, ent1)
    await call_service(hass, SERVICE_TOGGLE, ent2)
    await call_service(hass, SERVICE_TOGGLE, ent3)
    await call_service(hass, SERVICE_TOGGLE, ent4)
    await call_service(hass, SERVICE_TOGGLE, ent5)

    # entities without stop should be closed and with stop should be closing
    assert is_closed(hass, ent1)
    assert is_closing(hass, ent2)
    assert is_closed(hass, ent3)
    assert is_closed(hass, ent4)
    assert is_closing(hass, ent5)

    # call basic toggle services and set different cover position states
    await call_service(hass, SERVICE_TOGGLE, ent1)
    set_cover_position(ent2, 0)
    await call_service(hass, SERVICE_TOGGLE, ent2)
    await call_service(hass, SERVICE_TOGGLE, ent3)
    await call_service(hass, SERVICE_TOGGLE, ent4)
    set_cover_position(ent5, 15)
    await call_service(hass, SERVICE_TOGGLE, ent5)

    # entities should be in correct state depending on the SUPPORT_STOP feature and cover position
    assert is_open(hass, ent1)
    assert is_closed(hass, ent2)
    assert is_open(hass, ent3)
    assert is_open(hass, ent4)
    assert is_open(hass, ent5)

    # call basic toggle services
    await call_service(hass, SERVICE_TOGGLE, ent1)
    await call_service(hass, SERVICE_TOGGLE, ent2)
    await call_service(hass, SERVICE_TOGGLE, ent3)
    await call_service(hass, SERVICE_TOGGLE, ent4)
    await call_service(hass, SERVICE_TOGGLE, ent5)

    # entities should be in correct state depending on the SUPPORT_STOP feature and cover position
    assert is_closed(hass, ent1)
    assert is_opening(hass, ent2)
    assert is_closed(hass, ent3)
    assert is_closed(hass, ent4)
    assert is_opening(hass, ent5)


def call_service(hass, service, ent):
    """Call any service on entity."""
    return hass.services.async_call(
        cover.DOMAIN, service, {ATTR_ENTITY_ID: ent.entity_id}, blocking=True
    )


def set_cover_position(ent, position) -> None:
    """Set a position value to a cover."""
    ent._values["current_cover_position"] = position


def is_open(hass, ent):
    """Return if the cover is closed based on the statemachine."""
    return hass.states.is_state(ent.entity_id, STATE_OPEN)


def is_opening(hass, ent):
    """Return if the cover is closed based on the statemachine."""
    return hass.states.is_state(ent.entity_id, STATE_OPENING)


def is_closed(hass, ent):
    """Return if the cover is closed based on the statemachine."""
    return hass.states.is_state(ent.entity_id, STATE_CLOSED)


def is_closing(hass, ent):
    """Return if the cover is closed based on the statemachine."""
    return hass.states.is_state(ent.entity_id, STATE_CLOSING)


def _create_tuples(enum: Enum, constant_prefix: str) -> list[tuple[Enum, str]]:
    result = []
    for enum in enum:
        result.append((enum, constant_prefix))
    return result


def test_all() -> None:
    """Test module.__all__ is correctly set."""
    help_test_all(cover)


@pytest.mark.parametrize(
    ("enum", "constant_prefix"),
    _create_tuples(cover.CoverEntityFeature, "SUPPORT_")
    + _create_tuples(cover.CoverDeviceClass, "DEVICE_CLASS_"),
)
def test_deprecated_constants(
    caplog: pytest.LogCaptureFixture,
    enum: Enum,
    constant_prefix: str,
) -> None:
    """Test deprecated constants."""
    import_and_test_deprecated_constant_enum(
        caplog, cover, enum, constant_prefix, "2025.1"
    )


def test_deprecated_supported_features_ints(caplog: pytest.LogCaptureFixture) -> None:
    """Test deprecated supported features ints."""

    class MockCoverEntity(cover.CoverEntity):
        _attr_supported_features = 1

    entity = MockCoverEntity()
    assert entity.supported_features is cover.CoverEntityFeature(1)
    assert "MockCoverEntity" in caplog.text
    assert "is using deprecated supported features values" in caplog.text
    assert "Instead it should use" in caplog.text
    assert "CoverEntityFeature.OPEN" in caplog.text
    caplog.clear()
    assert entity.supported_features is cover.CoverEntityFeature(1)
    assert "is using deprecated supported features values" not in caplog.text
