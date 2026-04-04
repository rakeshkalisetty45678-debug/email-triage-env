---
title: Email Triage Env
emoji: 🐠
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: An RL environment for triaging emails — categorizing, priori
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
# Email Triage Environment

## Overview
An RL environment for triaging emails — categorizing, prioritizing, and actioning emails like a human would. Built for the OpenEnv RL Challenge.

## Tasks
| Task | Difficulty | Description |
|------|-----------|-------------|
| spam_detection | Easy | Identify whether email is spam or not |
| email_categorization | Medium | Categorize and prioritize emails |
| inbox_triage | Hard | Triage full inbox of 5 emails |

## Action Space
| Field | Values |
|-------|--------|
| category | spam, work, personal, newsletter, urgent |
| priority | high, medium, low |
| action | delete, reply, read, forward, archive |

## Observation Space
| Field | Description |
|-------|-------------|
| email.id | Email ID |
| email.subject | Email subject |
| email.sender | Sender address |
| email.body | Email body |
| step_number | Current step |
| task_description | Task description |

## Setup
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Baseline Scores
| Task | Score |
|------|-------|
| spam_detection | 0.85 |
| email_categorization | 0.70 |
| inbox_triage | 0.55 |

## API Endpoints
- POST /reset — Reset environment
- POST /step — Take action
- GET /state — Get current state
- GET /health — Health check