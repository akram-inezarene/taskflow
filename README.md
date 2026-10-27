# TaskFlow — Projet DevSecOps sur Kubernetes

Chaîne CI/CD complète sur un cluster K3s de 3 nœuds dans Google Cloud.

## Architecture

- 3 VM Google Cloud (Ubuntu 24.04), préparées avec **Ansible**
- Cluster **K3s** haute disponibilité : 3 nœuds server, etcd intégré
- **Traefik** (Ingress, HTTPS) et **Longhorn** (stockage répliqué sur les 3 nœuds)
- **Prometheus, Grafana, Alertmanager** : supervision et alertes
- **SonarQube** (qualité du code) et **Trivy** (failles de l'image)
- **Jenkins** (agents dans des pods Kubernetes) et **Helm** (déploiement)

## Pipeline

git push → tests (pytest) → SonarQube et Quality Gate → build de l'image → scan Trivy → Docker Hub → déploiement en préproduction → validation manuelle → déploiement en production

## Application

API FastAPI (`/api/tasks`, `/api/health`, `/metrics`), déployée avec le chart Helm de `chart/taskflow`.

## Tests de panne réalisés

- Suppression d'un pod : recréé automatiquement par Kubernetes
- Image inexistante : l'ancienne version continue de répondre, l'alerte PodBloque se déclenche, retour arrière avec `helm rollback`
- Test en échec : le pipeline s'arrête avant la construction de l'image, la production n'est pas touchée
