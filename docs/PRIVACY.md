# API privacy and rate limits

The API rate limit is approximately **30 requests per minute per client key**.
The key combines the client IP address and optional session ID. The in-memory
limiter runs before the response cache, so cached responses do not bypass the
limit.

## SQLite schema

The default database is `data/swasthya_setu.db` and is ignored by Git.

- `sessions`: SHA-256 session hash, creation time, and last-seen time.
- `messages`: session hash, role, SHA-256 message hash, and creation time.
- `feedback`: session hash, thumbs-up/down rating, optional comment, request ID,
  and creation time.

Raw session IDs and chat messages are not stored. The current implementation
does not automatically delete rows; operators should apply a retention policy
appropriate to their deployment and delete the SQLite file or old rows during
maintenance. Users should not submit names, addresses, phone numbers, or other
personal medical details.
