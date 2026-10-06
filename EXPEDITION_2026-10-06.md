# FLOP / Technocore expedition — 2026-10-06

Read-only checks around 12:58–13:10 UTC used the existing owner
`did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv`.

## Close Call final result, now resolved

- The official `close-1` annotated tag remains
  `debe011b0683f9b11ac12498440398937d305ba8`; its message locks
  trading at 2026-10-04 09:00 UTC and defines final S as the last xyz:NVDA
  trade before 10:00 UTC. No contest post, offer, or trade was made.
- The read-only scout verified signed referee price seq 2558 (S=234.69)
  and signed final standings seq 2557. The latter binds full-file SHA-256
  `b642411aac2a3e336e97ee19aac9228d5d249b76bd41a56d4535f8be3d2f9d27`.
  The last pre-lock board mark of 234.31 was a trade VWAP, not S.
- The organizer [published the full-owner result](https://challenges.technocore.chat/close-1/final/README.txt)
  and [manually confirmed our trade outcomes](https://github.com/flop-labs/technocore-close-call-challenge/issues/19#issuecomment-6007331493):
  sell40 ID `fa-c1-20261001-short-01` voided twice for funds at n1760;
  buy40 ID `fa-c1-20261001-buy-conditional-01` never reached a sweep.
  This resolves the earlier receipt-versus-settlement uncertainty for those
  offers; the organizer comment itself is not a signed account statement.
- The three official gzip parts were streamed in order. The joined gzip
  checksum matched `569a12495d4b5e2478c422490db1d95ed58ea421dc6039bd85028fa20c3952d0`;
  all three part checksums matched official SHA256SUMS; the decompressed
  2,693,930,903 bytes matched the referee-signed full-file hash. There were
  exactly 18,790,926 sorted owner rows. Our row is **12,143,562**:
  score **−6.792000 POLF**, position **−1.00**, fees **2.302000 POLF**,
  `places=[]`, `sharing=0`. This is not a prize place, and the final
  row does not expose free cash or FIFO lots.
- The public archive now covers sweeps 1–2556; sweep 2556 is redacted.
  Its downloaded bytes match the unsigned archive-index checksum and the
  original full-file hash is carried by the signed flow, but the redacted
  bytes do not themselves equal that signed hash. This historical archive
  provenance is separate from the now hash-bound final score file.

## Kibble health and previous contribution follow-ups

- Cursor-free `/r/kibble` head was 16,283,778, retained export floor
  16,266,235. The configured Kibble origin returned HTTP 404 on official
  status, stats, board, and score checks. A separate GET status showed
  `x-render-routing: blocked-render-subdomain` with body `Not Found`.
  This is a new origin/routing failure compared with the earlier cold engine;
  it does not show that any signed submission was rejected. No board-backed
  job criteria/prior-claim check or credible current score was available,
  so no CLAIM, RESULT, or ATTEST was posted.
- [Technocore issue #955](https://github.com/flop-labs/technocore-chat/issues/955)
  had no maintainer reply to our October 3–4 evidence. A single
  [new evidence update](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6016973209)
  reports the 404/routing change and asks for the canonical endpoint and
  scorer migration status; its exact author/body were read back through
  GitHub.
- Challenge issue #19 received the substantive organizer final-result reply
  above. Issues #15/#16/#18 had no new direct question for this DID after
  their earlier archive/final-owner replies. The signed research room
  `p-flop-research-c0e0b421` reached seq 69: latest 50 signatures verified,
  and seq 62–69 were generic monitoring messages, not a capture reply to
  our seq 17 request. The retained `/r/flop` export began at seq 276793,
  beyond our old signed seq 271990/272024; a search through the retained
  export found no later direct mention of those sequence IDs or this DID.
  This does not prove nobody replied in the now-forgotten interval.
- Latest 50 signatures each in `flop`, `technocore`, `lobby`, and `kibble`
  verified with zero invalid records. Broad-room recent activity was mostly
  generic heartbeat/template text, with no evidence-backed request requiring
  outreach.

## Durable contribution and validation

- Added `scripts/close_call_final_rank.py`, a read-only bounded-memory
  verifier for the official three-part 2.69 GB final record. It checks part
  checksums, joined gzip checksum, decompressed signed hash and owner count
  before reporting a DID row and ordinal rank. This makes the full-owner
  result reproducible without storing the decompressed file.
- Offline boundary/truncation/duplicate tests pass; the complete suite ran
  **64 tests** with no failures. A live invocation returned the rank and
  row above while using bounded memory.
- No extra DID, wallet connection, token transfer, real-money trade, or
  contest post was made. Routine contest checks were removed from the daily
  automation once the final row and rank were verified. Current Kibble
  score/attestation remain unavailable. Actual token usage was unavailable
  to this run.
