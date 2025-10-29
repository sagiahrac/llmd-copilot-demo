import os
import json
import re
from datetime import datetime
from typing import Optional, List, Dict
from kubernetes import config, client
from openshift.dynamic import DynamicClient


def create_dynamic_client() -> DynamicClient:
    k8s_client = config.new_client_from_config()
    return DynamicClient(k8s_client)

def get_epp_pod(dyn_client: DynamicClient, namespace: str, label_selector: str = 'inferencepool=gaie-kv-events-epp'):
    v1_pods = dyn_client.resources.get(api_version='v1', kind='Pod')
    pods = v1_pods.get(namespace=namespace, label_selector=label_selector)

    assert len(pods.items) == 1, "Expected exactly one epp"
    return pods.items[0]

def get_pod_logs(k8s_client: client.ApiClient, pod_name: str, namespace: str, tail_lines: int = 100) -> List[str]:
    core_v1 = client.CoreV1Api(api_client=k8s_client)
    pod_logs: str = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=tail_lines)
    log_lines = pod_logs.splitlines()
    return log_lines

def parse_collector_metrics_line(log_line: str) -> Optional[Dict]:
    """Parse a collector.go metrics line into a structured dictionary."""
    # Match the collector.go metrics pattern
    pattern = r'I(\d{4} \d{2}:\d{2}:\d{2}\.\d{6})\s+\d+ collector\.go:\d+\] "metrics beat" logger="metrics" (.+)'
    match = re.match(pattern, log_line)
    
    if not match:
        return None
    
    timestamp_str, metrics_str = match.groups()
    
    # Parse timestamp (format: MMDD HH:MM:SS.microseconds)
    # Assuming current year for simplicity
    current_year = datetime.now().year
    timestamp = datetime.strptime(f"{current_year}{timestamp_str}", "%Y%m%d %H:%M:%S.%f")
    
    # Parse metrics key-value pairs
    metrics = {"timestamp": timestamp.isoformat()}
    
    # Extract key=value pairs
    kv_pattern = r'(\w+)=([^\s]+)'
    for key, value in re.findall(kv_pattern, metrics_str):
        # Convert numeric values
        try:
            if '.' in value:
                metrics[key] = float(value)
            else:
                metrics[key] = int(value)
        except ValueError:
            metrics[key] = value
    
    return metrics

def parse_logs_for_collector_metrics(log_lines: List[str]) -> List[Dict]:
    """Parse log lines and extract collector.go metrics, sorted by time."""
    metrics_list = []
    
    for line in log_lines:
        parsed_metric = parse_collector_metrics_line(line)
        if parsed_metric:
            metrics_list.append(parsed_metric)
    
    # Sort by timestamp
    metrics_list.sort(key=lambda x: x['timestamp'])
    
    return metrics_list

def get_collector_metrics(namespace: str, tail_lines: int = 100) -> List[Dict]:
    """Get collector.go metrics from EPP pod logs."""
    dyn_client = create_dynamic_client()
    k8s_client = config.new_client_from_config()

    epp_pod = get_epp_pod(dyn_client, namespace)
    pod_name = epp_pod.metadata.name

    logs = get_pod_logs(k8s_client, pod_name, namespace, tail_lines)
    return parse_logs_for_collector_metrics(logs)

if __name__ == "__main__":
    namespace = os.environ.get('NAMESPACE', default='sage')
    print(f"Fetching collector metrics from EPP pod in namespace: {namespace}")

    metrics = get_collector_metrics(namespace)
    
    print(f"\nFound {len(metrics)} collector metrics entries:")
    for metric in metrics:
        print(json.dumps(metric, indent=2))
