# AI Customer Support Ticket System

An AI-powered customer support ticket analytics system built for the DOTMappers IT Pvt. Ltd. AI Engineer assessment.

## Features

- CSV-based customer support ticket ingestion
- Natural-language querying of ticket data
- AI-powered query understanding using Groq
- Ticket statistics and analytics
- Anomaly detection for unusually long resolution times
- Detection of unresolved High/Critical priority tickets older than 24 hours
- REST API using FastAPI
- Minimal web UI

## Dataset

The system uses `data/support_tickets.csv`.

The dataset contains 500 customer support tickets with the following fields:

- ticket_id
- created_at
- category
- priority
- status
- response_time_hrs
- resolution_time_hrs
- agent_id
- customer_rating
- issue_summary

## Architecture

```text
support_tickets.csv
        |
        v
TicketDataService
        |
        +----------------------+
        |                      |
        v                      v
 QueryService            AnomalyService
        |                      |
        v                      v
     Groq LLM            Anomaly Rules
        |                      |
        +----------+-----------+
                   |
                   v
              FastAPI
                   |
          +--------+--------+
          |                 |
          v                 v
      REST API           Web UI