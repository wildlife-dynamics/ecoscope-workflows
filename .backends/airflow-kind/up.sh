#!/bin/bash
# Based on: https://airflow.apache.org/docs/helm-chart/stable/quick-start.html

set -e

fmt='\e[1;34m%-6s\e[m\n'

requirements="docker kind helm kubectl"
printf ${fmt} "🐘 🦒 Checking requirements (${requirements})..."
for req in ${requirements[@]}; do
  if ! command -v ${req} &> /dev/null
    then
        printf "${req} is required but could not be found"
        printf "please install ${req} and then retry"
        exit 1
    fi
done
printf ${fmt} "🐘 🦒 ...all requirements present."


printf ${fmt} "🐘 🦒 Creating kind cluster..."
kind create cluster --config kind-cluster.yaml
kubectl cluster-info --context kind-kind
printf ${fmt} "🐘 🦒 ...cluster created!"

# TODO: Confirm dags volume mount

printf ${fmt} "🐘 🦒 Adding airflow helm repo..."
helm repo add apache-airflow https://airflow.apache.org
helm repo update
printf ${fmt} "🐘 🦒 ...helm repo added!"

printf ${fmt} "🐘 🦒 Creating k8s namespace..."
export NAMESPACE=example-namespace
kubectl create namespace $NAMESPACE
printf ${fmt} "🐘 🦒 ...k8s namespace created!"

printf ${fmt} "🐘 🦒 Installing airflow helm chart in cluster (this may take a few minutes)..."
export RELEASE_NAME=example-release
helm install $RELEASE_NAME apache-airflow/airflow \
  --namespace $NAMESPACE \
  -f helm-values.yaml
printf ${fmt} "🐘 🦒 ...successfully installed!"

# TODO: Confirm dags volume mounts

printf ${fmt} "🐘 🦒 Checking pod health..."
kubectl get pods --namespace $NAMESPACE
helm list --namespace $NAMESPACE

printf ${fmt} "🐘 🦒 Forwarding port..."
kubectl port-forward svc/$RELEASE_NAME-webserver 8080:8080 --namespace $NAMESPACE &
