from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

class PrometheusMessageSender:
    def __init__(self, url=None, user=None, password=None) -> None:
        url = url
        user = user
        password = password
        registry = CollectorRegistry()

    def auth_handler(self, url, method, timeout, headers, data, username, password):
        username = self.user
        password = self.password
        return basic_auth_handler(url, method, timeout, headers, data, username, password)
    
    def push_to_gateway(self, gauge_name=None, gauge_help=None, gague_value=None, batch_job_name=None):
        gauge = Gauge(gauge_name, gauge_help, registry=self.registry)
        gauge.set(gague_value)
        gauge.set_to_current_time()
        push_to_gateway(self.url, job=batch_job_name, registry=self.registry, handler=self.auth_handler)
