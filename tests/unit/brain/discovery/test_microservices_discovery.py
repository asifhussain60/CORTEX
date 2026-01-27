"""
Unit tests for microservices topology discovery.

Task: DISC-005
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.brain.discovery.microservices_discovery import (
    MicroservicesDiscovery,
    ServiceInfo,
    ContainerInfo,
    ServiceMeshType,
)


class TestMicroservicesDiscoveryInit:
    """Test microservices discovery initialization."""
    
    def test_init_creates_discovery(self) -> None:
        """Test that discovery can be instantiated."""
        discovery = MicroservicesDiscovery()
        assert discovery is not None
        assert hasattr(discovery, "discover")
    
    def test_supported_platforms_defined(self) -> None:
        """Test that supported platforms are defined."""
        discovery = MicroservicesDiscovery()
        platforms = discovery.get_supported_platforms()
        assert len(platforms) > 0
        assert "docker" in platforms
        assert "kubernetes" in platforms


class TestDockerComposeDiscovery:
    """Test Docker Compose service discovery."""
    
    def test_parse_docker_compose_file(self, tmp_path: Path) -> None:
        """Test parsing Docker Compose file."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.write_text("""
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - api
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://localhost/mydb
  redis:
    image: redis:alpine
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.parse_docker_compose(compose_file)
        
        assert result is not None
        assert len(result["services"]) == 3
        assert "web" in [s["name"] for s in result["services"]]
        assert "api" in [s["name"] for s in result["services"]]
        assert "redis" in [s["name"] for s in result["services"]]
    
    def test_extract_service_dependencies(self, tmp_path: Path) -> None:
        """Test extracting service dependencies."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.write_text("""
version: '3.8'
services:
  frontend:
    image: frontend:latest
    depends_on:
      - backend
      - cache
  backend:
    image: backend:latest
    depends_on:
      - database
  database:
    image: postgres:14
  cache:
    image: redis:alpine
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.parse_docker_compose(compose_file)
        
        # Find frontend service
        frontend = next(s for s in result["services"] if s["name"] == "frontend")
        assert "dependencies" in frontend
        assert len(frontend["dependencies"]) == 2
        assert "backend" in frontend["dependencies"]
        assert "cache" in frontend["dependencies"]


class TestKubernetesDiscovery:
    """Test Kubernetes resource discovery."""
    
    def test_parse_kubernetes_deployment(self, tmp_path: Path) -> None:
        """Test parsing Kubernetes deployment."""
        deploy_file = tmp_path / "deployment.yaml"
        deploy_file.write_text("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0
        ports:
        - containerPort: 8080
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.parse_kubernetes_manifest(deploy_file)
        
        assert result is not None
        assert result["kind"] == "Deployment"
        assert result["metadata"]["name"] == "my-app"
        assert result["spec"]["replicas"] == 3
    
    def test_parse_kubernetes_service(self, tmp_path: Path) -> None:
        """Test parsing Kubernetes service."""
        svc_file = tmp_path / "service.yaml"
        svc_file.write_text("""
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.parse_kubernetes_manifest(svc_file)
        
        assert result is not None
        assert result["kind"] == "Service"
        assert result["spec"]["type"] == "LoadBalancer"
        assert len(result["spec"]["ports"]) == 1


class TestServiceMeshDiscovery:
    """Test service mesh discovery."""
    
    def test_detect_istio_configuration(self, tmp_path: Path) -> None:
        """Test detecting Istio service mesh."""
        istio_file = tmp_path / "virtualservice.yaml"
        istio_file.write_text("""
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_service_mesh(tmp_path)
        
        assert result is not None
        assert result["type"] == "istio"
        assert len(result["resources"]) >= 1
    
    def test_detect_linkerd_configuration(self, tmp_path: Path) -> None:
        """Test detecting Linkerd service mesh."""
        linkerd_file = tmp_path / "servicemesh.yaml"
        linkerd_file.write_text("""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  annotations:
    linkerd.io/inject: enabled
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_service_mesh(tmp_path)
        
        assert result is not None
        assert result["type"] == "linkerd"


class TestAPIGatewayDiscovery:
    """Test API gateway discovery."""
    
    def test_detect_kong_gateway(self, tmp_path: Path) -> None:
        """Test detecting Kong API gateway."""
        kong_file = tmp_path / "kong.yml"
        kong_file.write_text("""
_format_version: "2.1"
services:
  - name: my-service
    url: http://backend:8000
    routes:
      - name: my-route
        paths:
          - /api
plugins:
  - name: rate-limiting
    config:
      minute: 100
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_api_gateway(tmp_path)
        
        assert result is not None
        assert result["type"] == "kong"
        assert len(result["services"]) >= 1
    
    def test_detect_nginx_ingress(self, tmp_path: Path) -> None:
        """Test detecting NGINX ingress controller."""
        ingress_file = tmp_path / "ingress.yaml"
        ingress_file.write_text("""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_api_gateway(tmp_path)
        
        assert result is not None
        assert result["type"] == "nginx-ingress"


class TestMessageBrokerDiscovery:
    """Test message broker discovery."""
    
    def test_detect_rabbitmq(self, tmp_path: Path) -> None:
        """Test detecting RabbitMQ."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.write_text("""
version: '3.8'
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: secret
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_message_brokers(tmp_path)
        
        assert result is not None
        assert len(result) >= 1
        assert result[0]["type"] == "rabbitmq"
        assert result[0]["port"] == 5672
    
    def test_detect_kafka(self, tmp_path: Path) -> None:
        """Test detecting Apache Kafka."""
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.write_text("""
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_message_brokers(tmp_path)
        
        assert result is not None
        assert len(result) >= 1
        kafka = next((b for b in result if b["type"] == "kafka"), None)
        assert kafka is not None
    
    def test_detect_redis_pubsub(self, tmp_path: Path) -> None:
        """Test detecting Redis Pub/Sub."""
        config_file = tmp_path / "redis.conf"
        config_file.write_text("""
port 6379
bind 0.0.0.0
# Redis Pub/Sub configuration
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.detect_message_brokers(tmp_path)
        
        assert result is not None
        redis = next((b for b in result if b["type"] == "redis"), None)
        assert redis is not None


class TestFullMicroservicesDiscovery:
    """Test complete microservices discovery."""
    
    def test_discover_complete_microservices_architecture(self, tmp_path: Path) -> None:
        """Test discovering complete microservices setup."""
        # Create Docker Compose
        (tmp_path / "docker-compose.yml").write_text("""
version: '3.8'
services:
  web:
    image: nginx
  api:
    build: .
  db:
    image: postgres
""")
        
        # Create Kubernetes manifest
        k8s_dir = tmp_path / "k8s"
        k8s_dir.mkdir()
        (k8s_dir / "deployment.yaml").write_text("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
""")
        
        discovery = MicroservicesDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert "docker_services" in result
        assert "kubernetes_resources" in result
        assert result["total_services"] >= 3
    
    def test_discover_handles_no_microservices(self, tmp_path: Path) -> None:
        """Test discovery with no microservices."""
        # Empty directory
        discovery = MicroservicesDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert result["total_services"] == 0
