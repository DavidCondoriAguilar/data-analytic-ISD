"""Sistema de logging y audit trail."""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

LOG_DIR = Path(__file__).parent.parent.parent / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class AuditLogger:
    """Logging estructurado con audit trail."""

    def __init__(self, operation: str):
        self.operation = operation
        self.timestamp = datetime.now()
        self.events: list = []
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger(f"audit.{self.operation}")
        self.logger.setLevel(logging.DEBUG)
        
        log_file = LOG_DIR / f"{self.operation}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.log"
        
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Registra un evento."""
        log_data = {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation,
            "message": message,
            "data": data or {}
        }
        self.events.append(log_data)
        
        if level == "SUCCESS":
            self.logger.info(f"✓ {message}", extra={"data": data})
        else:
            getattr(self.logger, level.lower())(message, extra={"data": data})

    def info(self, message: str, data: Optional[Dict] = None):
        self.log("INFO", message, data)

    def warning(self, message: str, data: Optional[Dict] = None):
        self.log("WARNING", message, data)

    def error(self, message: str, data: Optional[Dict] = None):
        self.log("ERROR", message, data)

    def success(self, message: str, data: Optional[Dict] = None):
        self.log("SUCCESS", message, data)

    def save_summary(self) -> Path:
        """Guarda resumen de la operación."""
        summary_file = LOG_DIR / f"summary_{self.operation}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = {
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat(),
            "events": self.events,
            "total_events": len(self.events)
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary_file


class ConfiabilidadTracker:
    """Tracking histórico de confiabilidad."""

    TRACK_FILE = LOG_DIR / "confiabilidad_history.json"

    @classmethod
    def record(cls, confiabilidad: float, total_records: int, valid_records: int,
               source_file: str, issues: list) -> Path:
        """Registra una ejecución."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "confiabilidad": confiabilidad,
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": total_records - valid_records,
            "source_file": source_file,
            "issues": issues,
            "certified": confiabilidad >= 99.9
        }

        history = cls._load_history()
        history["records"].append(record)
        history["last_updated"] = datetime.now().isoformat()
        history["total_runs"] = len(history["records"])

        if len(history["records"]) > 1:
            history["avg_confiabilidad"] = sum(r["confiabilidad"] for r in history["records"]) / len(history["records"])
            history["min_confiabilidad"] = min(r["confiabilidad"] for r in history["records"])
            history["max_confiabilidad"] = max(r["confiabilidad"] for r in history["records"])

        with open(cls.TRACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        return Path(cls.TRACK_FILE)

    @classmethod
    def _load_history(cls) -> Dict:
        if cls.TRACK_FILE.exists():
            with open(cls.TRACK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"records": []}

    @classmethod
    def get_summary(cls) -> Dict:
        """Obtiene resumen de historial."""
        history = cls._load_history()
        if not history.get("records"):
            return {"status": "sin datos"}

        last = history["records"][-1]
        return {
            "total_runs": history.get("total_runs", 0),
            "avg_confiabilidad": history.get("avg_confiabilidad", 0),
            "min_confiabilidad": history.get("min_confiabilidad", 0),
            "max_confiabilidad": history.get("max_confiabilidad", 0),
            "last_run": last["timestamp"],
            "last_confiabilidad": last["confiabilidad"],
            "last_certified": last.get("certified", False)
        }

    @classmethod
    def generate_report(cls) -> pd.DataFrame:
        """Genera DataFrame con historial."""
        history = cls._load_history()
        if not history.get("records"):
            return pd.DataFrame()
        
        df = pd.DataFrame(history["records"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=False)


class DataQualityAlert:
    """Sistema de alertas de calidad de datos."""

    ALERT_FILE = LOG_DIR / "alerts.json"

    @classmethod
    def check_and_alert(cls, confiabilidad: float, threshold: float = 99.9) -> Optional[Dict]:
        """Verifica umbrales y genera alerta si es necesario."""
        if confiabilidad < threshold:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "level": "CRITICAL" if confiabilidad < 90 else "WARNING",
                "confiabilidad": confiabilidad,
                "threshold": threshold,
                "message": f"Calidad de datos BAJO del umbral: {confiabilidad:.1f}% < {threshold}%",
                "action_required": True
            }
            cls._save_alert(alert)
            return alert
        return None

    @classmethod
    def _save_alert(cls, alert: Dict):
        alerts = []
        if cls.ALERT_FILE.exists():
            with open(cls.ALERT_FILE, 'r', encoding='utf-8') as f:
                alerts = json.load(f)

        alerts.append(alert)

        with open(cls.ALERT_FILE, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_active_alerts(cls, hours: int = 24) -> list:
        """Obtiene alertas activas de las últimas horas."""
        if not cls.ALERT_FILE.exists():
            return []

        with open(cls.ALERT_FILE, 'r', encoding='utf-8') as f:
            alerts = json.load(f)

        cutoff = datetime.now().timestamp() - (hours * 3600)
        return [a for a in alerts if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff]

    @classmethod
    def clear_resolved(cls, threshold_hours: int = 168):
        """Limpia alertas resueltas (más de 7 días)."""
        if not cls.ALERT_FILE.exists():
            return

        with open(cls.ALERT_FILE, 'r', encoding='utf-8') as f:
            alerts = json.load(f)

        cutoff = datetime.now().timestamp() - (threshold_hours * 3600)
        active = [a for a in alerts if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff]

        with open(cls.ALERT_FILE, 'w', encoding='utf-8') as f:
            json.dump(active, f, ensure_ascii=False, indent=2)
