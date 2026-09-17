import json

from .data_service import TicketDataService
from .groq_service import GroqService
from .anomaly_service import AnomalyService

class QueryService:
    def __init__(self):
        self.data_service = TicketDataService()
        self.groq_service = GroqService()
        self.anomaly_service = AnomalyService()

    def understand_question(self, question):
        """
        Use the LLM to identify what operation
        should be performed on the ticket data.
        """

        prompt = f"""
You are an AI assistant for a customer support ticket analytics system.

The available ticket fields are:

ticket_id
created_at
category
priority
status
response_time_hrs
resolution_time_hrs
agent_id
customer_rating
issue_summary

Convert the user's question into ONE JSON object.

Allowed operations:

1. count_status
   Example: "How many tickets are currently open?"
   JSON:
   {{"operation": "count_status", "status": "Open"}}

2. resolved_by_agent
   Example: "Which agent resolved the most tickets?"
   JSON:
   {{"operation": "resolved_by_agent"}}

3. average_rating
   Example: "What is the average customer rating for Technical category tickets?"
   JSON:
   {{"operation": "average_rating", "category": "Technical"}}

4. critical_not_resolved
   Example: "Show me all Critical tickets not resolved within 12 hours."
   JSON:
   {{"operation": "critical_not_resolved", "hours": 12}}

5. resolution_anomalies

Use this when the user asks about anomalies, abnormal resolution times,
unusually long resolution times, or resolution-time outliers.

Example: "Are there any anomalies in resolution times this week?"

JSON:
{{"operation": "resolution_anomalies"}}

6. unknown

   If the question does not match the available operations:

   JSON:
   {{"operation": "unknown"}}

Return ONLY valid JSON.
Do not add explanations.
Do not use markdown.

User question:
{question}
"""

        response = self.groq_service.ask(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"operation": "unknown"}

    def execute_question(self, question):
        """
        Understand the question using the LLM
        and execute the corresponding data operation.
        """

        intent = self.understand_question(question)

        operation = intent.get("operation")

        if operation == "count_status":

            status = intent.get("status")

            count = self.data_service.count_by_status(status)

            return {
                "question": question,
                "operation": operation,
                "answer": f"There are {count} {status.lower()} tickets.",
                "data": {
                    "status": status,
                    "count": count
                }
            }

        if operation == "resolved_by_agent":

            agent_counts = self.data_service.resolved_tickets_by_agent()

            if not agent_counts:
                return {
                    "question": question,
                    "operation": operation,
                    "answer": "No resolved tickets found.",
                    "data": {}
                }

            top_agent = next(iter(agent_counts))

            return {
                "question": question,
                "operation": operation,
                "answer": (
                    f"{top_agent} has resolved "
                    f"{agent_counts[top_agent]} tickets."
                ),
                "data": agent_counts
            }

        if operation == "average_rating":

            category = intent.get("category")

            average = self.data_service.average_customer_rating(
                category
            )

            if average is None:
                answer = "No customer ratings were found."
            else:
                answer = (
                    f"The average customer rating for "
                    f"{category} tickets is {average:.2f}."
                )

            return {
                "question": question,
                "operation": operation,
                "answer": answer,
                "data": {
                    "category": category,
                    "average_rating": average
                }
            }

        if operation == "critical_not_resolved":

            hours = intent.get("hours", 12)

            tickets = self.data_service.critical_not_resolved_within(
                hours
            )

            return {
                "question": question,
                "operation": operation,
                "answer": (
                    f"Found {len(tickets)} Critical tickets "
                    f"that are unresolved or took more than "
                    f"{hours} hours to resolve."
                ),
                "data": tickets
            }

        if operation == "resolution_anomalies":

            anomalies = self.anomaly_service.detect_long_resolution_times()

            return {
                "question": question,
                "operation": operation,
                "answer": (
                    f"Found {len(anomalies)} tickets with abnormally "
                    f"long resolution times."
                ),
                "data": anomalies
            }

        return {
            "question": question,
            "operation": "unknown",
            "answer": (
                "I could not identify a supported query "
                "for this question."
            ),
            "data": {}
        }


if __name__ == "__main__":

    service = QueryService()

    questions = [
        "How many tickets are currently open?",
        "Which agent resolved the most tickets?",
        "What is the average customer rating for Technical category tickets?",
        "Show me all Critical tickets not resolved within 12 hours."
    ]

    print("=" * 60)
    print("NATURAL LANGUAGE QUERY TEST")
    print("=" * 60)

    for question in questions:

        print("\nQuestion:")
        print(question)

        result = service.execute_question(question)

        print("\nAnswer:")
        print(result["answer"])

        print("\nOperation:")
        print(result["operation"])

    print("\n" + "=" * 60)