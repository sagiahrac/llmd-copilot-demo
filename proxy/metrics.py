import os
import json
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

if __name__ == "__main__":
    namespace = os.environ.get('NAMESPACE', default='sage')
    print(f"Fetching logs from EPP pod in namespace: {namespace}")

    dyn_client = create_dynamic_client()
    k8s_client = config.new_client_from_config()

    epp_pod = get_epp_pod(dyn_client, namespace)
    pod_name = epp_pod.metadata.name

    logs = get_pod_logs(k8s_client, pod_name, namespace)
    for log in logs:
        print(log)
