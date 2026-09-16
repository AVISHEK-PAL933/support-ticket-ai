import csv
from pathlib import Path
from datetime import datetime, timedelta


class TicketDataService:
    def __init__(self):
        self.data_path = (
            Path(__file__).parent.parent
            / "data"
            / "support_tickets.csv"
        )

        self.tickets = self._load_data()

    def _load_data(self):
        """Load and prepare ticket data from CSV."""
        tickets = []

        with open(
            self.data_path,
            "r",
            encoding="utf-8",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                row["created_at"] = datetime.strptime(
                    row["created_at"],
                    "%Y-%m-%d %H:%M"
                )

                row["response_time_hrs"] = float(
                    row["response_time_hrs"]
                )

                if row["resolution_time_hrs"].strip():
                    row["resolution_time_hrs"] = float(
                        row["resolution_time_hrs"]
                    )
                else:
                    row["resolution_time_hrs"] = None

                if row["customer_rating"].strip():
                    row["customer_rating"] = int(
                        row["customer_rating"]
                    )
                else:
                    row["customer_rating"] = None

                tickets.append(row)

        return tickets

    def get_all_tickets(self):
        """Return all tickets."""
        return self.tickets

    def get_ticket_count(self):
        """Return total number of tickets."""
        return len(self.tickets)

    def count_by_status(self, status):
        """Count tickets with a specific status."""
        return sum(
            1
            for ticket in self.tickets
            if ticket["status"].lower() == status.lower()
        )

    def count_by_priority(self, priority):
        """Count tickets with a specific priority."""
        return sum(
            1
            for ticket in self.tickets
            if ticket["priority"].lower() == priority.lower()
        )

    def average_customer_rating(self, category=None):
        """Calculate average customer rating."""
        ratings = []

        for ticket in self.tickets:
            if ticket["customer_rating"] is None:
                continue

            if category:
                if ticket["category"].lower() != category.lower():
                    continue

            ratings.append(ticket["customer_rating"])

        if not ratings:
            return None

        return sum(ratings) / len(ratings)

    def resolved_tickets_by_agent(self):
        """Count resolved tickets for each agent."""
        agent_counts = {}

        for ticket in self.tickets:
            if ticket["status"].lower() != "resolved":
                continue

            agent = ticket["agent_id"]

            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return dict(
            sorted(
                agent_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    def critical_not_resolved_within(self, hours):
        """
        Return Critical tickets that are unresolved
        or took more than the specified resolution time.
        """
        results = []

        for ticket in self.tickets:

            if ticket["priority"].lower() != "critical":
                continue

            # Still unresolved
            if ticket["resolution_time_hrs"] is None:
                results.append(ticket)
                continue

            # Resolved but took longer than threshold
            if ticket["resolution_time_hrs"] > hours:
                results.append(ticket)

        return results

    def get_resolution_times(self):
        """Return resolution times for resolved tickets."""
        return [
            ticket["resolution_time_hrs"]
            for ticket in self.tickets
            if ticket["resolution_time_hrs"] is not None
        ]


if __name__ == "__main__":

    service = TicketDataService()

    print("=" * 60)
    print("QUERY SERVICE TEST")
    print("=" * 60)

    print("\nTotal tickets:")
    print(service.get_ticket_count())

    print("\nOpen tickets:")
    print(service.count_by_status("Open"))

    print("\nResolved tickets:")
    print(service.count_by_status("Resolved"))

    print("\nAverage Technical customer rating:")
    print(service.average_customer_rating("Technical"))

    print("\nResolved tickets by agent:")
    print(service.resolved_tickets_by_agent())

    print("\nCritical tickets not resolved within 12 hours:")
    critical_tickets = service.critical_not_resolved_within(12)

    print(f"Count: {len(critical_tickets)}")

    for ticket in critical_tickets[:5]:
        print(
            ticket["ticket_id"],
            ticket["priority"],
            ticket["status"],
            ticket["resolution_time_hrs"]
        )

    print("=" * 60)