# Car Lease Contract for Home Assistant

[![Version][version-src]][version-href]
[![HACS: Custom][hacs-src]][hacs-href]
[![Downloads][downloads-src]][downloads-href]
[![Hits per month][hits-src]][hits-href]
[![code style: prettier][code-style-src]][code-style-href]

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

## Fixing an inaccurate baseline

Two baseline odometer readings are captured automatically and then reused
going forward:

- the reading that counts as **"0 km used"** for the whole contract
- the reading at the **start of the current calendar month** (used for
  "km left this month")

Both are captured at the moment they're first needed (initial setup, and
each time a new calendar month starts) - if the odometer's true reading at
that point in time isn't known, the integration falls back to whatever the
odometer currently shows. This means:

- Setting up the integration **mid-month** will make the first month's "km
  left this month" too optimistic (it think 0 km were driven yet this
  month, even if you're on day 20).
- Adding a contract **after the lease already started** without filling in
  the optional "Odometer reading at contract start" field has the same
  effect on "km left" as a whole.

The integration will try to recover the correct historical value from Home
Assistant's recorder before falling back to "current reading" - but this
only works if the recorder actually still has data that far back (its
default retention is just 10 days, via `recorder: purge_keep_days`), so it
mainly helps when HA happened to be offline right at a month boundary, not
for backfilling weeks of history.

If a value looks off, correct it directly with the **`lease_contract.set_baseline`**
service (Developer Tools → Actions in Home Assistant):

| Field | What it does |
|---|---|
| Target device | The car/contract device to correct |
| Contract start odometer | Overrides the whole-contract baseline |
| Month start odometer | Overrides this month's starting point |

For example, to fix "km left this month" being too high: work out what the
odometer read on the 1st of this month (current reading minus km you've
actually driven since then) and set that as **Month start odometer**. The
affected sensors update immediately.

## Releasing new versions

HACS discovers updates through **GitHub Releases** (git tags), not just
commits on `main`. This repo automates that with
`.github/workflows/release.yml`:

1. Bump `"version"` in `custom_components/lease_contract/manifest.json`
   (semantic versioning, e.g. `0.2.0` → `0.3.0`)
2. Commit and push to `main`
3. The workflow tags it `vX.Y.Z` and publishes a matching GitHub Release
   automatically — no manual tagging needed

Once a repo has releases, HACS shows a version dropdown when
installing/redownloading, with **"Latest version"** preselected by
default — so nothing further is needed to make "latest" the default
install target.

Two more workflows run on every push/PR and once a day:
`.github/workflows/hacs.yml` (HACS structure/manifest validation) and
`.github/workflows/hassfest.yml` (Home Assistant's own integration
validation). Keep an eye on their status — HACS's published-repository
review process expects both to pass.

### Troubleshooting: HACS shows a commit hash instead of a version

HACS falls back to showing the current commit SHA whenever a repository
has **no GitHub Releases yet** - it only shows a real version number once
at least one tagged Release exists. If you're seeing a commit hash:

1. Check the **Actions** tab on GitHub for a run of the "Release" workflow.
   If it never ran: the workflow only triggers on a push to `main` that
   touches `manifest.json`, so the very first release usually needs a
   manual kick via **Actions → Release → Run workflow** (the
   `workflow_dispatch` trigger).
2. If the run shows a red ✗: the most common cause is that the repository
   doesn't allow the workflow to create releases yet. Go to
   **Settings → Actions → General → Workflow permissions** and select
   **"Read and write permissions"**, then re-run the workflow.
3. Once a Release exists (check the repo's **Releases** page on GitHub),
   go back into HACS, open this integration, and use **Redownload** - that
   forces HACS to re-check the repository instead of waiting for its
   normal refresh cycle.

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

<!-- Badge reference links -->
[version-src]: https://img.shields.io/github/v/release/d-works42/ha-lease-contract.svg?style=flat-square
[version-href]: https://github.com/d-works42/ha-lease-contract/releases
[hacs-src]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square
[hacs-href]: https://github.com/hacs/integration
[downloads-src]: https://img.shields.io/github/downloads/d-works42/ha-lease-contract/total.svg?style=flat-square
[downloads-href]: https://github.com/d-works42/ha-lease-contract/releases
[hits-src]: https://hits.dwyl.com/d-works42/ha-lease-contract.svg?style=flat-square
[hits-href]: https://hits.dwyl.com/d-works42/ha-lease-contract
[code-style-src]: https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square
[code-style-href]: https://github.com/prettier/prettier
