import time
from collections import defaultdict
class AuthFailureAnalytics:
    def __init__(self):
        self.user_failures = defaultdict(int)
        self.reason_failures = defaultdict(int)
        self.failure_logs = []
        self.success_count = 0          

    def log_failure(self, username, reason):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.user_failures[username] += 1
        self.reason_failures[reason] += 1
        self.failure_logs.append({
            "username": username,
            "reason": reason,
            "time": timestamp
        })
    def log_success(self, username):
        self.success_count += 1
    def get_report(self):
        report = "\n========== AUTHENTICATION ANALYTICS ==========\n"
        report += f"Total Successful Logins : {self.success_count}\n"
        report += f"Total Failures         : {sum(self.user_failures.values())}\n"
        report += f"Failures Per User      : {dict(self.user_failures)}\n"
        report += f"Failures Per Reason    : {dict(self.reason_failures)}\n"
        report += "==============================================\n"
        return report
    def get_recent_failures(self, limit=10):
        return self.failure_logs[-limit:]