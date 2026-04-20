#!/usr/bin/env python3
import argparse
import random
import tempfile
from pathlib import Path

import httpx

TIERS = ["tier1", "tier2", "tier3", "free"]


def weighted_tier() -> str:
    # tweak distribution as you like
    return random.choices(
        population=TIERS,
        weights=[10, 20, 30, 40],  # tier1 rarer, free most common
        k=1,
    )[0]


def main():
    parser = argparse.ArgumentParser(description="Generate random users/tasks for demo queue.")
    parser.add_argument("--count", type=int, required=True, help="Number of random users/tasks to generate")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--filename-prefix", default="demo_file", help="Prefix for uploaded temp file names")
    args = parser.parse_args()

    if args.count <= 0:
        raise SystemExit("count must be > 0")

    upload_url = f"{args.base_url.rstrip('/')}/upload"
    created = []
    failures = 0

    with httpx.Client(timeout=30.0) as client:
        for i in range(1, args.count + 1):
            user_id = f"user_{i:04d}"
            tier = weighted_tier()

            # create temp file content
            tmp_content = f"demo payload for {user_id} ({tier})\n"
            with tempfile.NamedTemporaryFile("w+b", delete=False, suffix=".txt") as tf:
                tf.write(tmp_content.encode("utf-8"))
                tmp_path = Path(tf.name)

            file_name = f"{args.filename_prefix}_{i:04d}.txt"

            try:
                with open(tmp_path, "rb") as f:
                    resp = client.post(
                        upload_url,
                        data={"user_id": user_id, "tier": tier},
                        files={"file": (file_name, f, "text/plain")},
                    )
                if resp.status_code == 202:
                    body = resp.json()
                    created.append(
                        {
                            "user_id": user_id,
                            "tier": tier,
                            "task_id": body.get("task_id"),
                            "status": body.get("status"),
                        }
                    )
                    print(f"[OK] {user_id} tier={tier} task_id={body.get('task_id')}")
                else:
                    failures += 1
                    print(f"[FAIL] {user_id} tier={tier} status={resp.status_code} body={resp.text}")
            except Exception as e:
                failures += 1
                print(f"[ERR] {user_id} tier={tier} error={e}")
            finally:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass

    print("\n=== Summary ===")
    print(f"Requested: {args.count}")
    print(f"Created:   {len(created)}")
    print(f"Failures:  {failures}")

    # Tier summary
    by_tier = {t: 0 for t in TIERS}
    for c in created:
        by_tier[c["tier"]] += 1
    print("Tier distribution (created):")
    for t in TIERS:
        print(f"  {t}: {by_tier[t]}")


if __name__ == "__main__":
    main()
