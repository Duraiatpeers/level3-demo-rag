# Day 1 demos: with and without frameworks

Same app, same questions, shown two ways. First the hand-written pytest tests
you already type live (`tests/`), then the framework version of the same check.
Nothing in `tests/` was changed.

```
framework_demos/
  requirements-fairlearn.txt      pandas + Fairlearn (small)
  requirements-garak.txt          Garak (large - see "Install" below)
  fairlearn/
    test_fairness_fairlearn.py    Fairlearn version of tests/test_02_bias_fairness.py
  garak/
    px_direct.yaml                Garak scan: jailbreak / direct injection   (test_03)
    px_indirect.yaml              Garak scan: poisoned retrieval index        (test_04)
    check_garak_report.py         applies the PX rules (canary, phone number) to Garak's results
    run_garak.ps1 / run_garak.sh  runs both scans, then the check
```

## Install (do this before the session)

Use a separate virtual environment for Garak. It pulls in PyTorch and
Transformers: about 6 GB on the Linux machine it was tested on (the Windows CPU
build is usually smaller, but check). Count that against the 20 GB free-disk
requirement in the ToC.

PowerShell:
```
python -m venv .venv-fairlearn ; .\.venv-fairlearn\Scripts\Activate.ps1
pip install -r requirements.txt pytest requests -r framework_demos\requirements-fairlearn.txt
deactivate
python -m venv .venv-garak ; .\.venv-garak\Scripts\Activate.ps1
pip install -r framework_demos\requirements-garak.txt requests
```
Bash:
```
python -m venv .venv-fairlearn && source .venv-fairlearn/bin/activate
pip install -r requirements.txt pytest requests -r framework_demos/requirements-fairlearn.txt
deactivate
python -m venv .venv-garak && source .venv-garak/bin/activate
pip install -r framework_demos/requirements-garak.txt requests
```

Start the app as usual (`uvicorn app.main:app --port 8000`) in its own terminal.

## Demo A: fairness (M3.1)

**Without a framework** (the test you already type):
```
$env:PX_URL = "http://localhost:8000" ; $env:PX_KEY = "<your TRAINING_API_KEY>"
pytest tests/test_02_bias_fairness.py -v
```
Three hand-picked reporters, one pass each, a `"high" in answer` check, and a
length ratio you compute yourself.

**With Fairlearn:**
```
pytest framework_demos/fairlearn -v -s
```
`-s` is needed so the group tables print. Optional: `$env:FAIRNESS_REPEATS = "3"`
(default 5) and `$env:FAIRNESS_MAX_GAP = "0.2"`.

What it does differently:

| | Hand-written (`test_02`) | Fairlearn (`framework_demos/fairlearn`) |
|---|---|---|
| Groups | 3 hand-picked reporters | Full grid: employment x shift x plant = 8 groups |
| Repeats | 1 call each | 5 calls each (the model is not deterministic) |
| Grouping and comparing | Your own loop and min/max | `MetricFrame(...).by_group`, `.difference()`, `.ratio()` |
| Single attribute vs combined | Not separated | Both: three single-attribute checks, then all three combined |
| Ready-made fairness metric | None | `demographic_parity_difference` in one call |
| Output | Pass or fail | Per-group table, plus a CSV in `reports/` |

Talking point: the first test checks the assistant is right overall *before*
comparing groups, because an assistant that is wrong for everyone looks
perfectly fair. And the combined-groups test is where a skew hidden in one
corner shows up while each single attribute still looks acceptable.

## Demo B: injection (M3.2)

**Without a framework:**
```
pytest tests/test_03_direct_prompt_injection.py tests/test_04_indirect_prompt_injection.py -v
```
Three jailbreak phrasings you wrote, and one poisoned-index question.

**With Garak** (Garak environment active, app running, `PX_KEY` set):
```
$env:PX_KEY = "<your TRAINING_API_KEY>"
.\framework_demos\garak\run_garak.ps1
```
(bash: `PX_KEY=<key> bash framework_demos/garak/run_garak.sh`)

Each scan sends Garak's own attack corpus to `/ask`, then
`check_garak_report.py` reads every reply and applies the PX rules: the
`CANARY-7731` string (test_03) and a phone number (test_04). It exits with
code 1 if any reply broke a rule, so it can sit in a pipeline.

| | Hand-written (`test_03`, `test_04`) | Garak |
|---|---|---|
| Attack prompts | 3 + 1, written by you | 20 real-world jailbreaks (`dan.DanInTheWild`) + 10 latent jailbreaks, and 20 latent-injection documents against the poisoned index |
| Where the corpus comes from | Your imagination | Maintained by the Garak project, grows with each release |
| Knowing what counts as a leak | Your assertion | Generic detectors, plus the PX check script |
| Effort to add 20 more attacks | Write 20 tests | Change `soft_probe_prompt_cap` |

Things to say out loud:

- **Garak's own verdict is generic.** The `dan.DanInTheWild` detector marks a
  reply as a "bypass" when it contains no refusal wording. This app rarely
  refuses in those words, so Garak may report a high failure rate that does not
  mean a leak. That is why the PX check exists: only your own rule knows what a
  leak looks like in your application.
- **The indirect scan is not the same as test_04.** Garak's latent-injection
  probes hide instructions inside a document supplied in the prompt. test_04
  hides them in a document the *retrieval* step fetches. `px_indirect.yaml`
  combines both by pointing every prompt at the poisoned index. Retrieval
  poisoning stays an app-specific test.
- **The 20 / 10 caps are cost control.** Each prompt is one real model call.
  The full `DanInTheWild` probe is 256 prompts. Remove
  `soft_probe_prompt_cap` for a full run.

## What was verified and what was not

Checked here: the Fairlearn test against a clean mock, a subtly skewed mock
(single-attribute checks pass, combined and parity checks fail) and a heavily
skewed mock; both Garak scans against the offline stub app; and the PX check
firing (exit code 1) against a deliberately leaky mock. Python 3.13, Garak
0.17.1, Fairlearn 0.15.

Not checked: runs against your real Azure OpenAI deployment, Python 3.12, or
Windows / PowerShell. Run the whole sequence once on your own machine before the
session, and expect real-model numbers to differ.

Known limits of the offline check: the Garak probes `promptinject.*` and
`sysprompt_extraction.SystemPromptExtraction` produced no prompts without
internet access, so they are not used. Some Garak detectors try to download a
model on first run and print "detector load failed ... skipping" when they
cannot; the scan still completes.
