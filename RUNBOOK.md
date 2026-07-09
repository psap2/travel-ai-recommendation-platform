# Travel platform runbook

## Health
- Liveness: `GET /health` returns 200; `GET /metrics` returns Prometheus text.
- Watch `trip_stage_latency_seconds` p95 per stage (search / rank / suggest / llm).
- Watch `llm_calls_total{outcome="error"}` — a spike means OpenAI degraded.
- Watch CTR / booking_rate dashboards — a drop after a deploy means a bad ranking change.

## Common incidents
- **Slow planning**: check which stage's p95 climbed. LLM → smaller model or
  cache; rank → check Postgres indexes; search → check the FTS index + Redis hit rate.
- **`degraded: true` on every trip**: OpenAI is failing; verify `OPENAI_API_KEY`
  and status. Stays still serve — this is graceful degradation working.
- **CTR fell after a deploy**: a ranking-weight regression. Revert the weights;
  the feedback loop will confirm recovery in the next window.

## Deploy to AWS
- Build and push the image to ECR; run on ECS/Fargate behind an ALB.
- Use managed RDS (Postgres) and ElastiCache (Redis); inject secrets via SSM.
- Scale the API horizontally — it is stateless; Redis and Postgres are shared.
