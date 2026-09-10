# Payments Service High CPU Runbook

## Trigger
Start this procedure when average CPU utilization for the payments service remains above 85% for 10 minutes or when latency rises together with CPU saturation.

## Response procedure
1. Confirm whether traffic volume increased abnormally.
2. Compare CPU usage across replicas. One hot replica can indicate a stuck worker or uneven traffic distribution.
3. Check application latency, request rate, error rate, and queue depth before scaling.
4. Inspect recent deployments and feature-flag changes.
5. Review logs for retry storms, timeout loops, serialization errors, or unusually expensive requests.
6. If the service is healthy but capacity is insufficient, scale replicas according to the approved production autoscaling limit.
7. If high CPU began directly after a deployment and customer impact is increasing, use the rollback procedure rather than continuing to scale a faulty release.

## Safety note
Do not disable CPU limits or remove production resource controls during an incident without platform-team approval.
