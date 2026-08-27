terraform {
  required_version = ">= 1.7.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.14"
    }
  }
}

variable "namespace" {
  type        = string
  description = "Dedicated Kubernetes namespace for the GoAnalyze workload."
  default     = "goanalyze-government"
}

variable "kubeconfig" {
  type        = string
  description = "Optional kubeconfig path. Prefer workload identity or an injected CI kubeconfig in controlled environments."
  default     = null
  nullable    = true
}

variable "kube_context" {
  type        = string
  description = "Optional Kubernetes context name."
  default     = null
  nullable    = true
}

provider "kubernetes" {
  config_path    = var.kubeconfig
  config_context = var.kube_context
}

provider "helm" {
  kubernetes {
    config_path    = var.kubeconfig
    config_context = var.kube_context
  }
}

resource "kubernetes_namespace" "goanalyze" {
  metadata {
    name = var.namespace
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
      "pod-security.kubernetes.io/audit"   = "restricted"
      "pod-security.kubernetes.io/warn"    = "restricted"
      "app.kubernetes.io/part-of"          = "goanalyze-government"
    }
  }
}

resource "helm_release" "goanalyze" {
  name              = "goanalyze-government"
  namespace         = kubernetes_namespace.goanalyze.metadata[0].name
  chart             = "../helm/goanalyze-government"
  create_namespace  = false
  atomic            = true
  cleanup_on_fail   = true
  wait              = true
  wait_for_jobs     = true
  timeout           = 900
  dependency_update = false

  values = [
    file("${path.module}/values/goanalyze-values.yaml")
  ]
}
