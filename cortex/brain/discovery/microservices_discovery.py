"""
Microservices Topology Discovery

Discovers microservices architecture including Docker Compose, Kubernetes,
service mesh, API gateways, and message brokers.

Supports:
- Docker Compose service definitions
- Kubernetes resources (Deployments, Services, Ingress)
- Service mesh (Istio, Linkerd)
- API gateways (Kong, NGINX Ingress, Ambassador)
- Message brokers (RabbitMQ, Kafka, Redis Pub/Sub)

Task: DISC-005
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import logging
import re
import yaml
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

from cortex.brain.discovery import DiscoveryPlugin


logger = logging.getLogger(__name__)


class ServiceMeshType(Enum):
    """
    Service mesh types.
    
    Attributes:
        ISTIO: Istio service mesh
        LINKERD: Linkerd service mesh
        CONSUL: HashiCorp Consul service mesh
        UNKNOWN: Unknown or no service mesh
    """
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL = "consul"
    UNKNOWN = "unknown"


@dataclass
class ContainerInfo:
    """
    Container information.
    
    Attributes:
        name: Container name
        image: Container image
        ports: Exposed ports
        environment: Environment variables
    """
    name: str
    image: str
    ports: List[int] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceInfo:
    """
    Service information.
    
    Attributes:
        name: Service name
        type: Service type (docker, kubernetes, etc.)
        containers: Containers in service
        dependencies: Service dependencies
        replicas: Number of replicas
    """
    name: str
    type: str
    containers: List[ContainerInfo] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    replicas: int = 1


class MicroservicesDiscovery(DiscoveryPlugin):
    """
    Discovers microservices topology from repositories.
    
    Analyzes Docker Compose files, Kubernetes manifests, service mesh
    configurations, API gateway setups, and message broker definitions
    to map microservices architecture.
    
    Features:
    - Multi-platform support (Docker, Kubernetes)
    - Service dependency mapping
    - Service mesh detection (Istio, Linkerd)
    - API gateway discovery (Kong, NGINX)
    - Message broker detection (RabbitMQ, Kafka, Redis)
    
    Example:
        ```python
        discovery = MicroservicesDiscovery()
        topology = discovery.discover(Path("/my/repo"))
        
        for service in topology["docker_services"]:
            print(f"Service: {service['name']}")
        ```
    """
    
    def __init__(self) -> None:
        """Initialize microservices discovery."""
        self.supported_platforms = ["docker", "kubernetes", "service-mesh"]
        logger.info("MicroservicesDiscovery initialized")
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platforms.
        
        Returns:
            List of platform names
        """
        return self.supported_platforms
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover microservices topology in repository.
        
        Args:
            repo_path: Path to repository to scan
            
        Returns:
            Dictionary containing microservices topology
        """
        logger.info(f"Discovering microservices topology in {repo_path}")
        
        docker_services: List[Dict[str, Any]] = []
        kubernetes_resources: List[Dict[str, Any]] = []
        service_mesh_info: Optional[Dict[str, Any]] = None
        api_gateway_info: Optional[Dict[str, Any]] = None
        message_brokers: List[Dict[str, Any]] = []
        
        # Scan for Docker Compose files
        for compose_file in repo_path.rglob("docker-compose*.yml"):
            result = self.parse_docker_compose(compose_file)
            if result and "services" in result:
                docker_services.extend(result["services"])
        
        for compose_file in repo_path.rglob("docker-compose*.yaml"):
            result = self.parse_docker_compose(compose_file)
            if result and "services" in result:
                docker_services.extend(result["services"])
        
        # Scan for Kubernetes manifests
        for k8s_file in repo_path.rglob("*.yaml"):
            if "k8s" in str(k8s_file) or "kubernetes" in str(k8s_file):
                result = self.parse_kubernetes_manifest(k8s_file)
                if result:
                    kubernetes_resources.append(result)
        
        for k8s_file in repo_path.rglob("*.yml"):
            if "k8s" in str(k8s_file) or "kubernetes" in str(k8s_file):
                result = self.parse_kubernetes_manifest(k8s_file)
                if result:
                    kubernetes_resources.append(result)
        
        # Detect service mesh
        service_mesh_info = self.detect_service_mesh(repo_path)
        
        # Detect API gateway
        api_gateway_info = self.detect_api_gateway(repo_path)
        
        # Detect message brokers
        message_brokers = self.detect_message_brokers(repo_path)
        
        total_services = len(docker_services) + len(kubernetes_resources)
        
        logger.info(
            f"Discovered {len(docker_services)} Docker services, "
            f"{len(kubernetes_resources)} Kubernetes resources, "
            f"{len(message_brokers)} message brokers"
        )
        
        return {
            "docker_services": docker_services,
            "kubernetes_resources": kubernetes_resources,
            "service_mesh": service_mesh_info,
            "api_gateway": api_gateway_info,
            "message_brokers": message_brokers,
            "total_services": total_services,
            "total_brokers": len(message_brokers),
        }
    
    def parse_docker_compose(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse Docker Compose file.
        
        Args:
            file_path: Path to docker-compose.yml
            
        Returns:
            Parsed service information or None
        """
        try:
            with open(file_path) as f:
                compose = yaml.safe_load(f)
            
            if not compose or "services" not in compose:
                return None
            
            services = []
            for service_name, service_def in compose["services"].items():
                # Extract dependencies
                dependencies = []
                if "depends_on" in service_def:
                    if isinstance(service_def["depends_on"], list):
                        dependencies = service_def["depends_on"]
                    elif isinstance(service_def["depends_on"], dict):
                        dependencies = list(service_def["depends_on"].keys())
                
                # Extract ports
                ports = []
                if "ports" in service_def:
                    for port_mapping in service_def["ports"]:
                        if isinstance(port_mapping, str):
                            # Format: "80:80" or "8000:8000"
                            parts = port_mapping.split(":")
                            if len(parts) >= 2:
                                ports.append(int(parts[0]))
                
                services.append({
                    "name": service_name,
                    "image": service_def.get("image", ""),
                    "build": service_def.get("build", ""),
                    "ports": ports,
                    "dependencies": dependencies,
                    "environment": service_def.get("environment", {}),
                })
            
            logger.debug(f"Parsed Docker Compose: {file_path} ({len(services)} services)")
            
            return {
                "services": services,
                "version": compose.get("version", "unknown"),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse Docker Compose {file_path}: {e}")
            return None
    
    def parse_kubernetes_manifest(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse Kubernetes manifest file.
        
        Args:
            file_path: Path to Kubernetes YAML file
            
        Returns:
            Parsed Kubernetes resource or None
        """
        try:
            with open(file_path) as f:
                manifest = yaml.safe_load(f)
            
            if not manifest or "kind" not in manifest:
                return None
            
            # Only process specific Kubernetes resources
            valid_kinds = ["Deployment", "Service", "Ingress", "StatefulSet", "DaemonSet"]
            if manifest["kind"] not in valid_kinds:
                return None
            
            logger.debug(f"Parsed Kubernetes manifest: {file_path} (kind: {manifest['kind']})")
            
            return manifest
            
        except Exception as e:
            logger.warning(f"Failed to parse Kubernetes manifest {file_path}: {e}")
            return None
    
    def detect_service_mesh(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect service mesh configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Service mesh information or None
        """
        resources = []
        mesh_type = "unknown"
        
        # Check for Istio
        for istio_file in repo_path.rglob("*.yaml"):
            try:
                with open(istio_file) as f:
                    content = f.read()
                    if "istio.io" in content:
                        mesh_type = "istio"
                        manifest = yaml.safe_load(content)
                        if manifest and "kind" in manifest:
                            resources.append(manifest)
            except Exception:
                pass
        
        # Check for Linkerd
        for linkerd_file in repo_path.rglob("*.yaml"):
            try:
                with open(linkerd_file) as f:
                    content = f.read()
                    if "linkerd.io" in content:
                        mesh_type = "linkerd"
                        manifest = yaml.safe_load(content)
                        if manifest and "kind" in manifest:
                            resources.append(manifest)
            except Exception:
                pass
        
        if mesh_type != "unknown":
            logger.debug(f"Detected service mesh: {mesh_type}")
            return {
                "type": mesh_type,
                "resources": resources,
            }
        
        return None
    
    def detect_api_gateway(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect API gateway configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            API gateway information or None
        """
        # Check for Kong
        for kong_file in repo_path.rglob("kong*.yml"):
            try:
                with open(kong_file) as f:
                    config = yaml.safe_load(f)
                    if config and "services" in config:
                        logger.debug(f"Detected Kong gateway: {kong_file}")
                        return {
                            "type": "kong",
                            "services": config["services"],
                            "config_file": str(kong_file),
                        }
            except Exception:
                pass
        
        for kong_file in repo_path.rglob("kong*.yaml"):
            try:
                with open(kong_file) as f:
                    config = yaml.safe_load(f)
                    if config and "services" in config:
                        logger.debug(f"Detected Kong gateway: {kong_file}")
                        return {
                            "type": "kong",
                            "services": config["services"],
                            "config_file": str(kong_file),
                        }
            except Exception:
                pass
        
        # Check for NGINX Ingress
        for ingress_file in repo_path.rglob("ingress*.yaml"):
            try:
                with open(ingress_file) as f:
                    manifest = yaml.safe_load(f)
                    if manifest and manifest.get("kind") == "Ingress":
                        logger.debug(f"Detected NGINX Ingress: {ingress_file}")
                        return {
                            "type": "nginx-ingress",
                            "manifest": manifest,
                        }
            except Exception:
                pass
        
        return None
    
    def detect_message_brokers(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Detect message broker configurations.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of message broker information
        """
        brokers = []
        
        # Check for RabbitMQ in Docker Compose
        for compose_file in repo_path.rglob("docker-compose*.yml"):
            try:
                with open(compose_file) as f:
                    compose = yaml.safe_load(f)
                    if compose and "services" in compose:
                        for service_name, service_def in compose["services"].items():
                            image = service_def.get("image", "")
                            
                            # RabbitMQ
                            if "rabbitmq" in image:
                                ports = []
                                if "ports" in service_def:
                                    for port_mapping in service_def["ports"]:
                                        if isinstance(port_mapping, str):
                                            parts = port_mapping.split(":")
                                            if len(parts) >= 2:
                                                port = int(parts[0])
                                                if port == 5672:  # AMQP port
                                                    ports.append(port)
                                
                                brokers.append({
                                    "type": "rabbitmq",
                                    "name": service_name,
                                    "port": 5672 if 5672 in ports else None,
                                    "management_port": 15672,
                                })
                            
                            # Kafka
                            elif "kafka" in image:
                                brokers.append({
                                    "type": "kafka",
                                    "name": service_name,
                                    "port": 9092,
                                })
            except Exception:
                pass
        
        # Check for Redis
        for redis_file in repo_path.rglob("redis*.conf"):
            try:
                content = redis_file.read_text()
                if "port" in content:
                    brokers.append({
                        "type": "redis",
                        "name": "redis",
                        "port": 6379,
                        "config_file": str(redis_file),
                    })
            except Exception:
                pass
        
        logger.debug(f"Detected {len(brokers)} message brokers")
        return brokers
