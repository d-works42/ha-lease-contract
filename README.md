# Car Lease Contract for Home Assistant

Track one or more car leasing contracts in Home Assistant, based on an
existing odometer sensor for each car. Fully configured through the UI,
no YAML needed.

## Features

- Config-flow based setup, add as many contracts as you have cars
- Each contract is its own device with 5 sensors:
  - **Km left** — remaining allowance in the whole contract
  - **Monthly average km left** — remaining km divided over the full
    calendar months left until the contract ends
  - **Monthly average km used** — km driven so far divided over the
    full calendar months since the contract started
  - **Km left this month** — the current monthly average left, minus
    what's already been driven since the start of this calendar month
  - **Days left** — days remaining until the contract end date
- Recalculates immediately whenever the linked odometer sensor updates
  (no polling)
- Baseline odometer reading and current-month odometer reading survive
  Home Assistant restarts

## Installation

### Via HACS (custom repository)

1. In HACS, go to **Integrations** → the **⋮** menu → **Custom repositories**
2. Add this repository URL, category **Integration**
3. Install "Car Lease Contract" and restart Home Assistant

### Manual

Copy `custom_components/lease_contract` into your Home Assistant
`config/custom_components/` folder and restart.

## Setup

Go to **Settings → Devices & Services → Add Integration → Car Lease
Contract** and fill in:

| Field | Description |
|---|---|
| Name | Friendly name for this contract, e.g. "Tesla Model 3" |
| Odometer sensor | An existing sensor entity that reports the car's odometer in km |
| Maximum km in the contract | Total km allowance for the whole lease period |
| Contract start date | When the lease started |
| Contract end date | When the lease ends |
| Odometer reading at contract start (optional) | See note below |

Repeat the flow for each additional car/contract.

### About the starting odometer reading

The integration needs to know the odometer value that corresponds to
"0 km used" for this contract. If you set the integration up exactly
when the contract begins, leave the optional field empty — the current
odometer reading will be used as the baseline automatically. If the
contract already started earlier and the odometer has accumulated km
since then, fill in the odometer value it showed on the contract start
date for an accurate baseline.

This baseline is stored once, on first setup, and does not change
afterwards (even if you later edit or reinstall — removing and
re-adding the integration will reset it).

## Project layout

```
custom_components/lease_contract/
├── __init__.py        # entry setup/unload
├── config_flow.py      # UI configuration flow
├── const.py             # shared constants
├── calculations.py    # pure, unit-testable calculation logic
├── coordinator.py       # event-driven update coordinator + persistence
├── storage.py            # per-contract baseline storage
├── sensor.py              # the 5 sensor entities
├── manifest.json
├── strings.json
└── translations/en.json
```

## License

MIT — adjust as you like once this is in your own repository.
