from pick import pick  # install pick using `pip install pick`

from kubernetes import client, config
from kubernetes.client import configuration
import pandas as pd
import argparse, sys
from datetime import datetime

def main():
    # Handle the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns", help="The namespace to check")
    args=parser.parse_args()
    
    if str(args.ns) == "None":
        print("No namespace provided")
        exit(-1)

    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    option, _ = pick(contexts, title="Pick the context to load",
                     default_index=active_index)
    # Configs can be set in Configuration class directly or using helper
    # utility
    config.load_kube_config(context=option)

    print(f"Active host is {configuration.Configuration().host}")

    api = client.AppsV1Api()
    kube = client.AutoscalingV2Api()
    namespace = args.ns

    print("Listing HPAs with their deployments:")
    ret = kube.list_namespaced_horizontal_pod_autoscaler(namespace=namespace)
    
    df = pd.DataFrame(columns=["hpa_name","target_kind","target_name","reason","code"])

    for item in ret.items:

        hpa_name = item.metadata.name
        hpa_target_kind = item.spec.scale_target_ref.kind
        hpa_target_name = item.spec.scale_target_ref.name

        # print("Checking HPA - " + hpa_name)

        if hpa_target_kind == "Deployment":            
            try:
                dep = api.read_namespaced_deployment(name=hpa_target_name, namespace=namespace)
                # print(dep)
            except Exception as e:
                faulted_hpa = {"hpa_name": hpa_name, "target_kind": hpa_target_kind, "target_name": hpa_target_name, "reason": e.reason, "code": e.status}
                df = pd.concat([df, pd.DataFrame([faulted_hpa])], ignore_index=True)
                # print(e)
        
        if hpa_target_kind == "Stateful":
            try:
                state = api.read_namespaced_stateful_set(name=hpa_target_name, namespace=namespace)
                # print(state)
            except Exception as e:
                faulted_hpa = {"hpa_name": hpa_name, "target_kind": hpa_target_kind, "target_name": hpa_target_name, "reason": e.reason, "code": e.status}
                df = pd.concat([df, pd.DataFrame([faulted_hpa])], ignore_index=True)
                # print(e)

    print(df)
    df.to_csv("02-report-orphan-hpas-" + namespace + "-" + str(datetime.now()) + ".csv")


if __name__ == '__main__':
    main()