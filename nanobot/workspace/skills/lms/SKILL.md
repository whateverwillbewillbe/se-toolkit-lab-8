---
name: lms
description: Query the Learning Management System backend for labs, scores, learners, and analytics.
metadata: {"nanobot":{"emoji":"📚","requires":{"bins":["curl"],"env":["NANOBOT_LMS_BACKEND_URL","NANOBOT_LMS_API_KEY"]},"always":true}}
---

# LMS (Learning Management System)

Query the LMS backend API. All endpoints require the Bearer token from `$NANOBOT_LMS_API_KEY`.

Base URL: `$NANOBOT_LMS_BACKEND_URL`

## Health check

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/items/" | head -c 500
```

If the response is a JSON array, the backend is healthy. Count the items to report the item count.

## List labs

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/items/"
```

Filter results where `"type": "lab"`. Show their `title` and `id`.

## Pass rates for a lab

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/analytics/pass-rates?lab=LAB_ID"
```

Replace `LAB_ID` with the lab identifier (e.g., `lab-04`).

## List learners

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/learners/"
```

## Submission timeline

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/analytics/timeline?lab=LAB_ID"
```

## Group performance

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/analytics/groups?lab=LAB_ID"
```

## Top learners

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/analytics/top-learners?lab=LAB_ID&limit=5"
```

## Completion rate

```bash
curl -s -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/analytics/completion-rate?lab=LAB_ID"
```

## Sync pipeline

```bash
curl -s -X POST -H "Authorization: Bearer $NANOBOT_LMS_API_KEY" "$NANOBOT_LMS_BACKEND_URL/pipeline/sync"
```

## Tips

- Always ask the user which lab they mean if the query requires a `lab` parameter and none was given.
- Format numeric results nicely (percentages, counts).
- Keep responses concise.
