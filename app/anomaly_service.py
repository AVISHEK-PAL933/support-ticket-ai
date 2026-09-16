#from pathlib import Path
#import sys

# Allow importing data_service when running this file directly
#sys.path.append(str(Path(__file__).parent))

from .data_service import TicketDataService


class AnomalyService:

    def __init__(self):
        self.data_service = TicketDataService()
        self.tickets = self.data_service.get_all_tickets()

    def detect_long_resolution_times(self):
        """
        Detect unusually long resolution times using the IQR method.
        Only resolved tickets are considered.
        """

        resolution_times = [
            ticket["resolution_time_hrs"]
            for ticket in self.tickets
            if ticket["resolution_time_hrs"] is not None
        ]

        if not resolution_times:
            return []

        sorted_times = sorted(resolution_times)

        q1_index = len(sorted_times) // 4
        q3_index = (3 * len(sorted_times)) // 4

        q1 = sorted_times[q1_index]
        q3 = sorted_times[q3_index]

        iqr = q3 - q1

        upper_limit = q3 + (1.5 * iqr)

        anomalies = []

        for ticket in self.tickets:

            resolution_time = ticket["resolution_time_hrs"]

            if resolution_time is None:
                continue

            if resolution_time > upper_limit:
                anomalies.append({
                    "ticket_id": ticket["ticket_id"],
                    "priority": ticket["priority"],
                    "status": ticket["status"],
                    "resolution_time_hrs": resolution_time,
                    "threshold_hrs": round(upper_limit, 2),
                    "reason": "Abnormally long resolution time"
                })

        return anomalies

    def detect_unresolved_high_priority(self):
        """
        Detect unresolved High or Critical priority tickets.
        """

        if not self.tickets:
            return []

        # Use the latest timestamp in the dataset as the reference point.
        latest_created_at = max(
            ticket["created_at"]
            for ticket in self.tickets
        )

        anomalies = []

        for ticket in self.tickets:

            if ticket["status"].lower() not in ["open", "escalated"]:
                continue

            if ticket["priority"].lower() not in ["high", "critical"]:
                continue

            age_hours = (
                latest_created_at - ticket["created_at"]
            ).total_seconds() / 3600

            if age_hours > 24:

                anomalies.append({
                    "ticket_id": ticket["ticket_id"],
                    "priority": ticket["priority"],
                    "status": ticket["status"],
                    "created_at": ticket["created_at"],
                    "age_hours": round(age_hours, 2),
                    "reason": "Unresolved high-priority ticket older than 24 hours"
                })

        return anomalies

    def detect_all_anomalies(self):
        """
        Run all anomaly detection rules.
        """

        long_resolution = self.detect_long_resolution_times()
        unresolved_high_priority = self.detect_unresolved_high_priority()

        return {
            "long_resolution_times": long_resolution,
            "unresolved_high_priority": unresolved_high_priority
        }


if __name__ == "__main__":

    service = AnomalyService()

    print("=" * 60)
    print("ANOMALY DETECTION TEST")
    print("=" * 60)

    print("\n1. Abnormally long resolution times")

    long_resolution = service.detect_long_resolution_times()

    print(f"Anomalies found: {len(long_resolution)}")

    for anomaly in long_resolution[:10]:
        print(anomaly)

    print("\n2. Unresolved high-priority tickets older than 24 hours")

    high_priority = service.detect_unresolved_high_priority()

    print(f"Anomalies found: {len(high_priority)}")

    for anomaly in high_priority[:10]:
        print(anomaly)

    print("\n3. Total anomaly groups")

    all_anomalies = service.detect_all_anomalies()

    print(
        f"Long resolution: "
        f"{len(all_anomalies['long_resolution_times'])}"
    )

    print(
        f"Unresolved high priority: "
        f"{len(all_anomalies['unresolved_high_priority'])}"
    )

    print("=" * 60)