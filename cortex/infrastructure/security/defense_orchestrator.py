"""DefenseOrchestrator compatibility implementation for security tests."""

from typing import Any, Callable, Dict, List, Tuple


class DefenseOrchestrator:
    """Coordinates defense-in-depth validation layers."""

    LAYERS = {
        1: "Input Validation",
        2: "Rate Limiting",
        3: "Cryptography",
        4: "CORS/CSRF",
        5: "Audit Logging",
    }

    def __init__(self) -> None:
        self.layers: Dict[int, Dict[str, Any]] = {}
        self.violations: List[Dict[str, Any]] = []
        self.fail_secure_mode = True

    def register_layer(self, layer_id: int, validator_func: Callable[[Dict[str, Any]], bool]) -> None:
        if layer_id not in self.LAYERS:
            raise ValueError(f"Invalid layer ID: {layer_id}")
        self.layers[layer_id] = {
            "name": self.LAYERS[layer_id],
            "validator": validator_func,
            "status": "registered",
        }

    def validate_all_layers(self, request: Dict[str, Any]) -> Tuple[bool, List[int]]:
        failed_layers: List[int] = []

        for layer_id in sorted(self.layers.keys()):
            validator = self.layers[layer_id]["validator"]
            try:
                if not validator(request):
                    failed_layers.append(layer_id)
            except Exception as err:
                failed_layers.append(layer_id)
                self.violations.append({"layer": layer_id, "error": str(err)})

        return len(failed_layers) == 0, failed_layers

    def apply_fail_secure_defaults(self) -> Dict[str, Any]:
        return {
            "default_action": "DENY",
            "explicit_allow_required": True,
            "audit_all_denials": True,
        }

    def validate_no_single_point_of_failure(self) -> bool:
        return len(self.layers) >= 5

    def get_layer_status(self) -> Dict[int, Dict[str, Any]]:
        return {
            layer_id: {"name": layer["name"], "status": layer["status"]}
            for layer_id, layer in self.layers.items()
        }

    def coordinate_layer_response(self, layer_violations: List[int]) -> Dict[str, Any]:
        if not layer_violations:
            return {"action": "allow", "reason": "all_layers_passed"}
        return {
            "action": "deny",
            "reason": "security_violation",
            "violated_layers": layer_violations,
        }


__all__ = ["DefenseOrchestrator"]
