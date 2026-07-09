# Pinterest — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Official docs confirm a single REST API covering organic content (Pins/Boards), ads campaigns/targeting/reporting, product catalogs/shopping ads, conversions, and analytics—hence Broad. Auth is OAuth 2.0 after gated app registration (business account required, form submission, daily review for Trial tier; temporary product-limited tokens only post-approval). Python SDK and quickstart exist but do not remove the review gate. Docs are clear so not Blocked, yet review/verification elevates buildability to Hard (vs pure self-serve OAuth). Next action Needs Outreach because API is public but entry requires approval. Rate limits only from third-party (zernio); no official numbers in fetched text. Preseed was none so no confirmation/contradiction. Confidence high on core access model from primary docs, slightly tempered by third-party rate data and incomplete tier details.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** — Business account + email verify + app registration form; trial access reviewed each business day
- recommended_next_action: **Needs Outreach**
- confidence: **0.88**

## Evidence URLs (whitelist-enforced)
- https://developers.pinterest.com
- https://developers.pinterest.com/docs/getting-started/authentication/
- https://developers.pinterest.com/
- https://zernio.com/blog/pinterest-api
