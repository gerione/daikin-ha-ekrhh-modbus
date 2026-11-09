"""Tests keeping the translation files in sync with the register tables."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import AIR2AIR, ALTHERMA_3, ALTHERMA_4, make_entry, setup_entry

ROOT = Path(__file__).parent.parent
COMPONENT = ROOT / "custom_components" / "daikin_ha_ekrhh_modbus"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_english_translation_matches_strings() -> None:
    """translations/en.json is a copy of strings.json."""
    assert _load(COMPONENT / "translations" / "en.json") == _load(
        COMPONENT / "strings.json"
    )


def test_generated_names_are_current(tmp_path: Path) -> None:
    """Running tools/gen_translations.py would not change the entity names."""
    copy = tmp_path / "component"
    shutil.copytree(COMPONENT, copy)
    subprocess.run(
        [sys.executable, "-I", str(ROOT / "tools" / "gen_translations.py"), str(copy)],
        check=True,
        capture_output=True,
    )
    assert _load(copy / "strings.json") == _load(COMPONENT / "strings.json")


@pytest.mark.parametrize("version", [ALTHERMA_3, ALTHERMA_4, AIR2AIR])
async def test_every_entity_has_a_name(hass: HomeAssistant, unit, version) -> None:
    """Each entity's translation key has a name in the translations."""
    names = _load(COMPONENT / "strings.json")["entity"]
    entry = make_entry(version, additional_zone=True)
    await setup_entry(hass, entry)
    for entity in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id):
        assert entity.translation_key in names[entity.domain], entity.entity_id
        assert hass.states.get(entity.entity_id).name.startswith("daikin ")
