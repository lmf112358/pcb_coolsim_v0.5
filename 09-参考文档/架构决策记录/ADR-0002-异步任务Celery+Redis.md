# ADR-0002: Async Tasks with Celery + Redis

**Status:** Accepted
**Date:** 2026-07-09
**Decision Makers:** Tech Lead, Backend Lead, Architect

---

## Context

Several operations in PCB-CoolSim are long-running:
- Dynamic simulation: 8760h × 3 years × 1000 rooms → 20-30 seconds
- Weather data fetching: External API calls → 1-2 minutes
- Report generation: PDF/Excel export → 10-30 seconds
- Batch calculations: 1000 rooms → 5-10 seconds

These operations should not block the API response or degrade user experience.

## Decision

**Use Celery + Redis for async task processing:**

- **Celery:** Distributed task queue for async job execution
- **Redis:** Message broker + result backend + caching
- **Pattern:** Fire-and-forget with WebSocket notifications

**Implementation:**
```python
# Task submission
task = calculate_dynamic_simulation.delay(project_id, params)
return Response({'task_id': task.id}, status=202)

# Client subscribes to WebSocket
ws://host/ws/tasks/{task_id}/

# Worker publishes progress
channel_layer.group_send(task_id, {'type': 'progress', 'data': {...}})
```

## Rationale

1. **Non-blocking:** Users can continue working while calculations run
2. **Scalable:** Can add more workers for increased throughput
3. **Reliable:** Celery provides retry mechanisms and task persistence
4. **Real-time Updates:** WebSocket integration for progress tracking
5. **Well-Established:** Mature ecosystem with good Django integration

## Consequences

### Positive
- Responsive UI during long operations
- Scalable architecture
- Real-time progress feedback
- Task retry on failure

### Negative
- Additional infrastructure (Redis)
- More complex deployment
- Need to handle async state in frontend

### Risks
- Redis failure → Mitigated by Redis persistence and monitoring
- Task queue backlog → Mitigated by worker auto-scaling

## Alternatives Considered

### Alternative 1: Synchronous Processing
**Rejected:** Blocks API response, poor UX for long operations

### Alternative 2: Django Channels with Background Threads
**Rejected:** Less robust, harder to scale, no built-in retry

### Alternative 3: AWS SQS + Lambda
**Rejected:** Vendor lock-in, higher latency for task dispatch

## Related

- PRD: Section 17.2 (Async Task Architecture)
- Database: Task result tables
- Infrastructure: Docker Compose includes Redis and Celery workers
