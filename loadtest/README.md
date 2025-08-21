# Tailspin Toys Load Testing (k6)

This folder contains a k6 script to stress the deployed Tailspin Toys client until failure thresholds are reached.

## Prereqs
- k6 installed locally (https://k6.io/docs/get-started/installation/)

## Test target
Default base URL: `http://4.187.182.42`
Override with env var `BASE_URL`.

## Run (stress: ramp until breaking point)
```bash
# From repo root
k6 run loadtest/k6/tailspin-stress.test.js

# With custom base URL and think time (sec)
BASE_URL="http://YOUR-LB-IP" THINK_TIME=0.1 \
  k6 run loadtest/k6/tailspin-stress.test.js
```

## Output
- A summary JSON is written to `loadtest/results.json` after the run.

## Safety notes
- This script is aggressive and can generate large load. Use against non-production targets or with appropriate approvals.
- Your AKS LoadBalancer may take time to scale; consider adjusting stages in the script if needed.
