"""Write entity names from const.py into strings.json and translations/en.json."""
import json, re, sys
from pathlib import Path

comp = Path(sys.argv[1])
ns = {}
exec((comp / "const.py").read_text(encoding="utf-8"), ns)
D = ns["DOMAIN"]

def tkey(key):
    return key.strip().lower().removeprefix(f"{D}_")

def rows(*names, name_i=1, key_i=2):
    for n in names:
        for r in ns[n]:
            yield r[name_i], r[key_i]

platforms = {
    "sensor": list(rows("ALTHERMA_3_INPUT", "ALTHERMA_3_INPUT_ADDITIONAL_ZONE",
                        "ALTHERMA_4_INPUT", "ALTHERMA_4_INPUT_ADDITIONAL_ZONE"))
              + [(v[0], v[1]) for v in ns["A2A_SENSOR_TYPES"].values()]
              + [tuple(ns["FAULT_CODE_SENSOR"][:2])],
    "binary_sensor": list(rows("ALTHERMA_3_INPUT_BINARY", "ALTHERMA_4_INPUT_BINARY",
                               "ALTHERMA_4_DISCRETE_INPUTS", "ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE")),
    "number": list(rows("ALTHERMA_3_HOLDING", "ALTHERMA_3_HOLDING_ADDITIONAL_ZONE",
                        "ALTHERMA_4_HOLDING", "ALTHERMA_4_HOLDING_ADDITIONAL_ZONE"))
              + list(rows("DAIKIN_A2A_NUMBER_TYPES", name_i=0, key_i=1)),
    "select": list(rows("ALTHERMA_3_HOLDING_SELECT", "ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE",
                        "ALTHERMA_4_HOLDING_SELECT", "ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE"))
              + list(rows("DAIKIN_A2A_SELECT_TYPES", name_i=0, key_i=1)),
    "switch": list(rows("ALTHERMA_4_COILS", "ALTHERMA_4_COILS_ADDITIONAL_ZONE")),
    "climate": [tuple(ns["CLIMATE_ENTITY"])],
    "water_heater": [tuple(ns["WATER_HEATER_ENTITY"])],
}

entity = {}
for platform, items in platforms.items():
    out = {}
    for name, key in items:
        k = tkey(key)
        assert re.fullmatch(r"[a-z0-9_-]+", k), k
        assert k not in out or out[k]["name"] == name.strip(), (platform, k)
        out[k] = {"name": name.strip()}
    entity[platform] = out

strings = json.loads((comp / "strings.json").read_text(encoding="utf-8"))
strings["entity"] = entity
text = json.dumps(strings, indent=4, ensure_ascii=False) + "\n"
for target in ("strings.json", "translations/en.json"):
    (comp / target).write_text(text, encoding="utf-8", newline="\n")
print({p: len(v) for p, v in entity.items()})
