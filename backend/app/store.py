"""In-memory store for the MVP — swap for Postgres/Redis when persistence
across restarts matters."""
import threading
import uuid


class InMemoryStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.alerts: dict[str, dict] = {}
        self.incidents: dict[str, dict] = {}

    def add_alert(self, alert: dict) -> dict:
        alert_id = str(uuid.uuid4())
        record = {**alert, "id": alert_id, "status": "new"}
        with self._lock:
            self.alerts[alert_id] = record
        return record

    def get_alert(self, alert_id: str) -> dict | None:
        return self.alerts.get(alert_id)

    def list_alerts(self) -> list[dict]:
        return list(self.alerts.values())

    def update_alert_status(self, alert_id: str, status: str):
        with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id]["status"] = status

    def add_incident(self, incident: dict) -> dict:
        incident_id = str(uuid.uuid4())
        record = {**incident, "id": incident_id}
        with self._lock:
            self.incidents[incident_id] = record
        return record

    def get_incident(self, incident_id: str) -> dict | None:
        return self.incidents.get(incident_id)

    def list_incidents(self) -> list[dict]:
        return list(self.incidents.values())


store = InMemoryStore()
