# src.entry_point.pagination

Pagination Manager for Chat Output

Provides simple persistence for paged outputs to avoid chat length limits.

Pages are stored per conversation under:
  cortex-brain/corpus-callosum/output_pages/{conversation_id}.json

Schema:
{
  "conversation_id": str,
  "continuation_id": str,
  "total": int,
  "current": int,   # 0-based index of last served page
  "pages": [str],
  "created": iso timestamp
}
