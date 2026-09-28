# Provider recovery and database evidence

Use this workflow when a harness covers settlement, refunds, compensation, shipping labels or any
durable provider operation. The project's testing and security standards and its active runbooks own
the release requirements; this procedure helps assemble the evidence.

## Fixtures and assertions

1. **Keep provider fixtures internally consistent.** Model the charge account, charge amount,
   application fee, measured balance-transaction fee details, fee refund list and local durable facts
   together. A database reimbursement timestamp does not stand in for a provider refund. Seed the
   exact refund id, fee id, amount, currency where applicable, order/reason metadata and original
   account. Derive aggregate refunded totals from those facts. Keep changed profile accounts distinct
   so an accidental fallback to the member's current account fails visibly.
2. **Exercise recovery reads as well as writes.** A second invocation must run against the same
   operation and updated provider/store state. Supply exact-object retrieval and complete list
   responses; a broad list route must not swallow a single-object retrieval. Simulate a successful
   provider operation whose response or local persistence is lost, then assert one provider mutation
   across attempts and completion of the missing local consequence. Distinguish retry after proved
   rejection from replay of a started operation with an unknown outcome.
3. **Assert conservation at the boundaries.** Cover zero, partial and full credit, missing measured
   fees, fee greater than service fee, and fee greater than the entire application fee. Assert actual
   provider amounts, account scopes, operation identities and ordering, plus buyer/seller/platform
   balances. Separate nominal-payment compensation from cancellation compensation when they are
   different obligations; summing two expected amounts alone cannot prove their identities.

## Provider success followed by local failure

For durable payment or label handlers, inject a failure after provider success and business-row
persistence but before the final operation commit. Keep both the provider object and database state
alive across a second request. Assert that the retry repairs the operation commit and issues no
second provider mutation; an early return from a saved URL or refund id must not bypass recovery.
Also assert pending or failed provider outcomes remain distinct from settled money.

## What the harness cannot prove

Mocks do not validate a provider's current payload schema or database locking.

4. **Use real disposable database evidence for SQL claims.** Mocked stored-procedure acknowledgements
   prove handler wiring, not authorization, transactionality or concurrency. Replay the real migration
   chain and run SQL/concurrency tests separately. If the corpus fails, run the same failing suite
   against a clean control on the base branch before labeling it a regression. An identical failure
   on the base branch does not establish a baseline defect: first match the official runner's
   bootstrap, including roles, default privileges, extensions, pre-migration setup and execution
   order. For Supabase, inspect the pinned CLI's initialization steps as well as migration SQL;
   omitted API/default-ACL setup can make both control and feature runs fail while the official CI
   passes. Reproduce through the official runner or prove bootstrap parity before attributing the
   failure. Record runner limitations separately from product defects; do not weaken the test or call
   the corpus green.
5. **Validate the provider contract separately.** Keep harnesses offline. When the authorized task
   includes provider verification, use an isolated real provider Sandbox with test credentials and
   designated fixtures, following the active runbook. Keep these canaries separate from offline
   harnesses, require explicit sandbox or local credentials, track fixture ids immediately for
   `finally` cleanup, and state which delivery, payment and identity checks were simulated. Compare
   actual provider objects and ledger consequences, including retry of the same operation. Report
   exactly what was exercised and cleaned up; a mocked handler pass does not prove Sandbox settlement,
   and Sandbox success does not prove production configuration. Never store secrets or customer data
   in skill examples or reports.
6. **Re-run after contract tightening.** A new exact-fact guard can expose an impossible old fixture.
   First confirm the failure demonstrates missing fixture evidence rather than a product regression;
   then repair the provider/store history without bypassing the guard. Send the final test result to
   any independent reviewer so their replay uses the same stabilized implementation.
