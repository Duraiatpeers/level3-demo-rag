"""Run after deployment:  python smoke_test.py https://<your-app>.azurewebsites.net <TRAINING_API_KEY>
Set AOAI_ENDPOINT, AOAI_KEY, AOAI_CHAT first (your own model) unless REQUIRE_LEARNER_MODEL=0 on the app."""
import sys, requests
base, key = sys.argv[1].rstrip("/"), (sys.argv[2] if len(sys.argv) > 2 else "")
import os
H = {"X-API-Key": key}
if os.environ.get("AOAI_ENDPOINT"):      # learner-style call: your own model in headers
    H.update({"X-Model-Endpoint": os.environ["AOAI_ENDPOINT"], "X-Model-Key": os.environ["AOAI_KEY"],
              "X-Model-Chat-Deployment": os.environ["AOAI_CHAT"]})
def ask(q, **kw): 
    r = requests.post(f"{base}/ask", headers=H, json={"question": q, **kw}, timeout=60); r.raise_for_status(); return r.json()
h = requests.get(f"{base}/health", timeout=30).json(); print("health:", h)
assert h["status"] == "ok"
checks = []
r = ask("What is the maximum operating pressure of the PX-100?", prompt_version="v1")
checks.append(("fact: PX-100 limit says 10 bar, not 15 bar", "10 bar" in r["answer"] and "15 bar" not in r["answer"]))
checks.append(("citations present", len(r["citations"]) > 0))
r = ask("What is the warranty period of the PX-100?", prompt_version="v1")
checks.append(("missing evidence admitted (v1)", any(p in r["answer"].lower() for p in ("do not state", "could not find", "not found", "no information", "does not"))))
r = ask("Raise a service request for PX100-L3-007. It keeps overheating.", session="smoke")
checks.append(("tool drafted, not created", bool(r["tool_calls"]) and all(c["status"] == "pending_confirmation" for c in r["tool_calls"])))
r = ask("Yes, please submit it.", session="smoke")
checks.append(("created after confirmation", r["tool_calls"] and r["tool_calls"][0]["status"] == "created"))
for name, ok in checks: print("PASS" if ok else "FAIL", "-", name)
sys.exit(0 if all(ok for _, ok in checks) else 1)
