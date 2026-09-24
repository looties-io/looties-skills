# Merchant API recipes

Read this when you need to query or change a Google Merchant Center account programmatically: Step 1
(ask Google first), Step 2 (one source of truth) and Step 10 (scheduled status check).

Host: `https://merchantapi.googleapis.com`. Account name format: `accounts/{ACCOUNT_ID}`.
OAuth scope: `https://www.googleapis.com/auth/content`.

Endpoints marked **(used by a working monitor)** were exercised by a production status check. The
others follow the same API's published shape; confirm them in Google's current reference before
relying on them, because this API has moved versions recently.

## Contents

1. Access traps
2. Authentication
3. Register the GCP project
4. Read the account (audit)
5. Change the sources (deliberate)
6. Triage recipe

## 1. Access traps

These four cost hours each. Check them before debugging anything else.

| Symptom | Cause | Fix |
|---|---|---|
| 401 "API keys are not supported by this API" | An API key (`AIza...`) was used | Use a principal: an OAuth user refresh token or a service account |
| 401 `GCP_NOT_REGISTERED` | The Cloud project is not registered with the merchant account | Call `developerRegistration:registerGcp` (section 3). It is an API call, not a console setting |
| 409 `V1BETA_RAMP_DOWN` | Calling the retired `v1beta` paths | Use the `v1` paths (`/accounts/v1/`, `/products/v1/`, `/datasources/v1/`) |
| Errors from the Content API for Shopping | The predecessor API has been shut down | Do not enable or target it; migrate to Merchant API |

One false lead worth knowing: a "Web application" OAuth client accepts `http://localhost` redirect URIs
(Google's documentation exempts localhost from the HTTPS rule), so a local consent flow does not
require creating a separate desktop client.

## 2. Authentication

For a scheduled job, mint a refresh token once for a user who has access to the merchant account,
store it with the OAuth client id and secret as CI secrets, and exchange it for an access token at
run time:

```bash
curl -s https://oauth2.googleapis.com/token \
  -d client_id="$CLIENT_ID" \
  -d client_secret="$CLIENT_SECRET" \
  -d refresh_token="$REFRESH_TOKEN" \
  -d grant_type=refresh_token
# -> { "access_token": "...", "expires_in": 3599, ... }
```

Make a failed exchange exit non-zero with a distinct code. A revoked token is itself a finding:
nothing has been watching the account since it broke.

Never print the tokens, and keep the refresh token file out of the repository with owner-only
permissions.

## 3. Register the GCP project

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://merchantapi.googleapis.com/accounts/v1/accounts/$ACCOUNT/developerRegistration:registerGcp" \
  -d '{"developerEmail": "<a developer contact address>"}'
```

In practice it takes effect immediately. Run it once per project and account pair.

## 4. Read the account (audit)

All read-only. Page through results with `pageToken` / `nextPageToken`.

```text
GET /accounts/v1/accounts/{ACCOUNT}/issues                               (used by a working monitor)
GET /datasources/v1/accounts/{ACCOUNT}/dataSources?pageSize=50           (used by a working monitor)
GET /datasources/v1/accounts/{ACCOUNT}/dataSources/{ID}/fileUploads/latest (used by a working monitor)
GET /products/v1/accounts/{ACCOUNT}/products?pageSize=250                (used by a working monitor)
GET /accounts/v1/accounts/{ACCOUNT}/autofeedSettings
```

What to read in each response:

- **issues**: `accountIssues[]`. Any entry is a stop-everything finding.
- **dataSources**: each source's `input` (`FILE`, `API`, `UI`, `AUTOFEED`), `displayName`, and
  `fileInput` (present only for fetched files, with its fetch URL and schedule). Filter on
  `fileInput` to find your feed. No such source means your published feed reaches nobody.
- **fileUploads/latest**: `processingState` (want `SUCCEEDED`), `uploadTime`, `itemsTotal`, `issues`.
  Read `itemsTotal`, not `itemsCreated`: the latter only appears when a fetch introduced new offers,
  so a healthy steady-state fetch omits it.
- **products**: in `v1` there is no separate product-status call; each product carries
  `productStatus`, with `destinationStatuses[]` (`reportingContext`, `approvedCountries`,
  `pendingCountries`, `disapprovedCountries`) and `itemLevelIssues[]` (`code`, `severity`,
  `attribute`, `reportingContext`, `applicableCountries`, `resolution`).
- **autofeedSettings**: `enableProducts`. `true` while you publish your own feed means two sources
  describe the same catalogue.

## 5. Change the sources (deliberate)

These write to the account. Announce them, do them once, and re-read afterwards.

```text
POST   /datasources/v1/accounts/{ACCOUNT}/dataSources          create a primary product source
DELETE /datasources/v1/accounts/{ACCOUNT}/dataSources/{ID}     remove a leftover source
POST   /datasources/v1/accounts/{ACCOUNT}/dataSources/{ID}:fetch  trigger a fetch now
PATCH  /accounts/v1/accounts/{ACCOUNT}/autofeedSettings?updateMask=enableProducts  turn autofeed off
```

A primary source for a fetched file declares, at minimum: a display name; the primary product data
source settings (feed label, content language, target countries); and the file input with its fetch
URL, frequency, time of day and time zone. Set destinations deliberately (for example free listings
on, Shopping ads off) instead of accepting defaults.

Schedule your own monitor after Google's fetch time, and your feed rebuild before it.

## 6. Triage recipe

1. Pull every product, flatten `itemLevelIssues`, and count by `(severity, code, attribute)`.
2. Separately count products with any `disapprovedCountries` per `reportingContext`.
3. Sort `DISAPPROVED` codes by count. Take the top one, find the single root cause (usually one
   missing attribute or one account setting), fix it, wait for the next fetch, re-read.
4. Only after disapprovals reach zero, look at `DEMOTED`. Record `NOT_IMPACTED` codes once and move on.
5. Keep "approved somewhere" as a headline number. Zero approved with zero disapprovals usually
   means nothing was fetched, not that everything is pending.
