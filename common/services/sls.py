from django.conf import settings
from aliyun.log.logclient import LogClient
from aliyun.log.getlogsrequest import GetLogsRequest
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AliyunLog(object):
    client = None

    def __init__(self):
        self.client = LogClient(settings.ALIYUN['LOG_ENDPOINT'],
                                settings.ALIYUN['ACCESS_KEY'],
                                settings.ALIYUN['ACCESS_SECRET'])

    def request(self, logstore=None, project=None, *args, **kwargs):
        logstore = logstore or settings.ALIYUN['LOG_LOGSTORE']
        project = project or settings.ALIYUN['LOG_PROJECT']
        return GetLogsRequest(project, logstore, *args, **kwargs)

    def request_all(self, logstore=None, project=None, *args, **kwargs):
        return self.client.get_log_all(logstore=logstore, project=project, *args, **kwargs)

    def fetch_banned_history_list(self, host, from_time, to_time, filter_limit=500, offset=0, reverse=False, ip=None, jail=None):
        if not isinstance(host, (list, str)):
            raise ValueError(f"Expected 'host' to be a list or a string, got {type(host)}")

        if isinstance(host, str):
            host = [host]

        if not host:
            return []

        host_filter = [f"""__tag__:__hostname__:{h}""" for h in host]
        host_filter_str = f"({' or '.join(host_filter)})"
        
        query = f"""* and {host_filter_str} and action='Ban'"""
        
        # Add jail and IP filter if provided
        if jail:
            query += f" and jail='{jail}'"
        if ip:
            query += f" and ip='{ip}'"
        
        query += f" | select ip, hostname, time, jail order by time desc"

        request = self.request(logstore='fail2ban', fromTime=from_time.timestamp(), toTime=to_time.timestamp(),
                               query=query, line=filter_limit, offset=offset, reverse=reverse)

        try:
            res = self.client.get_logs(request)
            return res.get_logs() or []
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []

    def fetch_banned_counts(self, host, filter_limit=10000, offset=0, reverse=False):
        if not isinstance(host, (list, str)):
            raise ValueError(f"Expected 'host' to be a list or a string, got {type(host)}")

        if isinstance(host, str):
            host = [host]

        if not host:
            return {}

        host_filter = [f"""__tag__:__hostname__:{h}""" for h in host]
        host_filter_str = f"({' or '.join(host_filter)})"
        
        current_time = datetime.utcnow()
        seven_days_ago = current_time - timedelta(days=7)

        queries = {
            'total_banned': f"""* and {host_filter_str} and action='Ban' | select count(*) as count""",
            'unban_last_7_days': f"""* and {host_filter_str} and action='Unban' | select count(*) as count""",
            'ban_last_7_days': f"""* and {host_filter_str} and action='Ban' | select count(*) as count"""
        }

        total_banned_count = self._fetch_logs(queries['total_banned'], 0, current_time, filter_limit, offset, reverse)
        unban_last_7_days_count = self._fetch_logs(queries['unban_last_7_days'], seven_days_ago, current_time, filter_limit, offset, reverse)
        ban_last_7_days_count = self._fetch_logs(queries['ban_last_7_days'], seven_days_ago, current_time, filter_limit, offset, reverse)

        return {
            'total_banned': total_banned_count,
            'unban_last_7_days': unban_last_7_days_count,
            'ban_last_7_days': ban_last_7_days_count
        }

    def _fetch_logs(self, query, from_time, to_time, filter_limit, offset, reverse):
        """Helper function to safely fetch logs and extract the count."""
        try:
            request = self.request(logstore='fail2ban', fromTime=(from_time if from_time == 0 else from_time.timestamp()), toTime=to_time.timestamp(),
                                   query=query, line=filter_limit, offset=offset, reverse=reverse)
            res = self.client.get_logs(request)
            return self._extract_count_from_response(res)
        except Exception as e:
            print(f"Error fetching logs for query '{query}': {e}")
            return 0

    def _extract_count_from_response(self, response):
        """Helper function to safely extract the count from the response."""
        try:
            logs = response.get_logs()
            if logs:
                count = logs[0].__dict__.get('contents', {}).get('count', 0)
                return int(count)
            return 0
        except Exception as e:
            print(f"Error extracting count from response: {e}")
            return 0
