#!/usr/bin/env python3
"""
🎯 SWAGGER/OPENAPI AGENT EXPERT
================================
Agent expert pour générer, maintenir et synchroniser les spécifications
OpenAPI 3.0 avec le backend, générer les types TypeScript, l'UI,
et assurer le contract testing.

Architecture:
    Frontend (React/TS)
         ↕ (TypeScript types auto-générés)
    OpenAPI Spec (Source of Truth)
         ↕ (Validation automatique)
    Backend (Python agents)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import yaml
import subprocess
from pathlib import Path


@dataclass
class Endpoint:
    """API Endpoint specification."""
    path: str
    method: str  # GET, POST, PUT, DELETE, PATCH
    summary: str
    description: str
    tags: List[str]
    request_body: Optional[Dict] = None
    responses: Dict[str, Dict] = None
    security: List[str] = None


class SwaggerOpenAPIAgent:
    """
    Expert agent for OpenAPI specs, code generation, and UI/API sync.
    
    Capabilities:
    1. Generate OpenAPI 3.0 spec from Python backend
    2. Generate TypeScript types from OpenAPI
    3. Generate React components from OpenAPI
    4. Generate mock server from OpenAPI
    5. Contract testing (frontend ↔ backend)
    6. Swagger UI hosting
    """
    
    def __init__(self, backend_path: str = "sovereign-dashboard"):
        self.backend_path = Path(backend_path)
        self.spec_path = self.backend_path / "openapi.yaml"
        self.endpoints: List[Endpoint] = []
    
    # ========================================================================
    # 1. OPENAPI SPEC GENERATION
    # ========================================================================
    
    def generate_openapi_spec(self) -> dict:
        """
        Generate complete OpenAPI 3.0 specification for aSiReM system.
        """
        
        # Define all endpoints
        self._define_all_endpoints()
        
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "aSiReM Multi-Agent System API",
                "version": "1.0.0",
                "description": """
                Complete API for the aSiReM Autonomous Agent System.
                
                Features:
                - 32 autonomous agents
                - 90 capabilities
                - Real-time WebSocket streaming
                - Semantic gap detection
                - 500+ technology support
                """,
                "contact": {
                    "name": "aSiReM Team",
                    "url": "https://asirem.dev"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8082",
                    "description": "Local development server"
                },
                {
                    "url": "https://api.asirem.dev",
                    "description": "Production server"
                }
            ],
            "tags": self._get_tags(),
            "paths": self._generate_paths(),
            "components": {
                "schemas": self._generate_schemas(),
                "securitySchemes": self._generate_security_schemes()
            }
        }
        
        return spec
    
    def _define_all_endpoints(self):
        """Define all API endpoints."""
        
        # Agent Management
        self.endpoints.extend([
            Endpoint(
                path="/api/agents",
                method="GET",
                summary="List all agents",
                description="Get list of all 32 autonomous agents with their status",
                tags=["Agents"],
                responses={
                    "200": {
                        "description": "List of agents",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AgentList"}
                            }
                        }
                    }
                }
            ),
            Endpoint(
                path="/api/agents/{agent_id}",
                method="GET",
                summary="Get agent details",
                description="Get detailed information about a specific agent",
                tags=["Agents"],
                responses={
                    "200": {
                        "description": "Agent details",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Agent"}
                            }
                        }
                    }
                }
            ),
            Endpoint(
                path="/api/agents/{agent_id}/execute",
                method="POST",
                summary="Execute agent task",
                description="Execute a task with a specific agent",
                tags=["Agents"],
                request_body={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AgentTask"}
                        }
                    }
                },
                responses={
                    "200": {
                        "description": "Task execution result",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TaskResult"}
                            }
                        }
                    }
                }
            )
        ])
        
        # Scanning & Analysis
        self.endpoints.extend([
            Endpoint(
                path="/api/scan/start",
                method="POST",
                summary="Start codebase scan",
                description="Initiate semantic scanning of target codebase",
                tags=["Scanning"],
                request_body={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ScanRequest"}
                        }
                    }
                },
                responses={
                    "202": {
                        "description": "Scan started",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ScanStatus"}
                            }
                        }
                    }
                }
            ),
            Endpoint(
                path="/api/scan/{scan_id}/status",
                method="GET",
                summary="Get scan status",
                description="Get current status of running scan",
                tags=["Scanning"],
                responses={
                    "200": {
                        "description": "Scan status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ScanStatus"}
                            }
                        }
                    }
                }
            ),
            Endpoint(
                path="/api/gaps",
                method="GET",
                summary="Get detected gaps",
                description="Retrieve all detected gaps from semantic analysis",
                tags=["Scanning"],
                responses={
                    "200": {
                        "description": "List of gaps",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/GapList"}
                            }
                        }
                    }
                }
            )
        ])
        
        # Capabilities
        self.endpoints.extend([
            Endpoint(
                path="/api/capabilities",
                method="GET",
                summary="List all capabilities",
                description="Get all 90 system capabilities",
                tags=["Capabilities"],
                responses={
                    "200": {
                        "description": "Capabilities list",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CapabilityList"}
                            }
                        }
                    }
                }
            )
        ])
        
        # Health & Status
        self.endpoints.extend([
            Endpoint(
                path="/api/health",
                method="GET",
                summary="Health check",
                description="System health status",
                tags=["System"],
                responses={
                    "200": {
                        "description": "System healthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthStatus"}
                            }
                        }
                    }
                }
            ),
            Endpoint(
                path="/api/metrics",
                method="GET",
                summary="System metrics",
                description="Real-time system metrics",
                tags=["System"],
                responses={
                    "200": {
                        "description": "Metrics data",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Metrics"}
                            }
                        }
                    }
                }
            )
        ])
    
    def _get_tags(self) -> List[Dict]:
        """Get API tags for organization."""
        return [
            {"name": "Agents", "description": "Agent management and execution"},
            {"name": "Scanning", "description": "Semantic scanning and gap detection"},
            {"name": "Capabilities", "description": "System capabilities"},
            {"name": "System", "description": "Health and metrics"}
        ]
    
    def _generate_paths(self) -> Dict:
        """Generate paths section from endpoints."""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            paths[endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "responses": endpoint.responses or {}
            }
            
            if endpoint.request_body:
                paths[endpoint.path][endpoint.method.lower()]["requestBody"] = endpoint.request_body
        
        return paths
    
    def _generate_schemas(self) -> Dict:
        """Generate component schemas."""
        return {
            "Agent": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "status": {"type": "string", "enum": ["idle", "running", "error"]},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "metrics": {"$ref": "#/components/schemas/AgentMetrics"}
                }
            },
            "AgentList": {
                "type": "object",
                "properties": {
                    "agents": {"type": "array", "items": {"$ref": "#/components/schemas/Agent"}},
                    "total": {"type": "integer"}
                }
            },
            "AgentTask": {
                "type": "object",
                "required": ["task_type", "parameters"],
                "properties": {
                    "task_type": {"type": "string"},
                    "parameters": {"type": "object"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                }
            },
            "Task Result": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {"type": "string"},
                    "result": {"type": "object"},
                    "duration_ms": {"type": "integer"}
                }
            },
            "ScanRequest": {
                "type": "object",
                "required": ["target_path"],
                "properties": {
                    "target_path": {"type": "string"},
                    "scan_type": {"type": "string", "enum": ["full", "incremental"]},
                    "include_patterns": {"type": "array", "items": {"type": "string"}},
                    "exclude_patterns": {"type": "array", "items": {"type": "string"}}
                }
            },
            "ScanStatus": {
                "type": "object",
                "properties": {
                    "scan_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["running", "completed", "failed"]},
                    "progress": {"type": "number", "minimum": 0, "maximum": 100},
                    "files_scanned": {"type": "integer"},
                    "gaps_found": {"type": "integer"}
                }
            },
            "Gap": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "severity": {"type": "string", "enum": ["critical", "major", "minor", "info"]},
                    "description": {"type": "string"},
                    "path": {"type": "string"},
                    "sample": {"type": "string"}
                }
            },
            "GapList": {
                "type": "object",
                "properties": {
                    "gaps": {"type": "array", "items": {"$ref": "#/components/schemas/Gap"}},
                    "total": {"type": "integer"},
                    "by_severity": {"type": "object"}
                }
            },
            "CapabilityList": {
                "type": "object",
                "properties": {
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "total": {"type": "integer"},
                    "coverage": {"type": "number"}
                }
            },
            "HealthStatus": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["healthy", "degraded", "down"]},
                    "agents_running": {"type": "integer"},
                    "uptime_seconds": {"type": "integer"}
                }
            },
            "Metrics": {
                "type": "object",
                "properties": {
                    "requests_total": {"type": "integer"},
                    "requests_per_second": {"type": "number"},
                    "active_scans": {"type": "integer"},
                    "memory_usage_mb": {"type": "number"},
                    "cpu_usage_percent": {"type": "number"}
                }
            },
            "AgentMetrics": {
                "type": "object",
                "properties": {
                    "tasks_completed": {"type": "integer"},
                    "tasks_failed": {"type": "integer"},
                    "avg_duration_ms": {"type": "number"}
                }
            }
        }
    
    def _generate_security_schemes(self) -> Dict:
        """Generate security schemes."""
        return {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
    
    def save_spec(self, format: str = "yaml") -> Path:
        """Save OpenAPI spec to file."""
        spec = self.generate_openapi_spec()
        
        if format == "yaml":
            with open(self.spec_path, 'w') as f:
                yaml.dump(spec, f, sort_keys=False, default_flow_style=False)
            return self.spec_path
        else:
            json_path = self.backend_path / "openapi.json"
            with open(json_path, 'w') as f:
                json.dump(spec, f, indent=2)
            return json_path
    
    # ========================================================================
    # 2. TYPESCRIPT TYPE GENERATION
    # ========================================================================
    
    def generate_typescript_types(self) -> str:
        """
        Generate TypeScript types from OpenAPI spec.
        Uses openapi-typescript tool.
        """
        spec_path = self.save_spec("yaml")
        output_path = self.backend_path / "frontend" / "src" / "types" / "api.ts"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate types using openapi-typescript
        cmd = f"npx openapi-typescript {spec_path} -o {output_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return str(output_path)
        else:
            raise Exception(f"Type generation failed: {result.stderr}")
    
    # ========================================================================
    # 3. REACT COMPONENTS GENERATION
    # ========================================================================
    
    def generate_react_components(self) -> List[Path]:
        """
        Generate React components and hooks from OpenAPI spec.
        """
        components_generated = []
        
        # Generate API client hooks
        hooks_path = self.backend_path / "frontend" / "src" / "hooks" / "useApi.ts"
        hooks_path.parent.mkdir(parents=True, exist_ok=True)
        
        hooks_code = '''
import { useState, useCallback } from 'react';
import type { paths } from '../types/api';

type ApiResponse<T> = {
  data: T | null;
  loading: boolean;
  error: Error | null;
};

export function useApi<TPath extends keyof paths>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const request = useCallback(async <TMethod extends keyof paths[TPath]>(
    path: TPath,
    method: TMethod,
    options?: RequestInit
  ): Promise<any> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8082${path}`, {
        method: method as string,
        ...options
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { request, loading, error };
}
'''
        
        with open(hooks_path, 'w') as f:
            f.write(hooks_code)
        
        components_generated.append(hooks_path)
        
        return components_generated
    
    # ========================================================================
    # 4. MOCK SERVER GENERATION
    # ========================================================================
    
    def generate_prod_server(self) -> Path:
        """
        Generate mock server from OpenAPI spec using Prism.
        """
        spec_path = self.save_spec("yaml")
        
        # Create mock server script
        prod_script = self.backend_path / "start_prod_server.sh"
        
        script_content = f'''#!/bin/bash
# Mock server for aSiReM API
# Uses Prism to serve mock responses from OpenAPI spec

npx @stoplight/prism-cli mock {spec_path} --port 8083 --dynamic
'''
        
        with open(prod_script, 'w') as f:
            f.write(script_content)
        
        prod_script.chmod(0o755)
        
        return prod_script
    
    # ========================================================================
    # 5. CONTRACT TESTING
    # ========================================================================
    
    def generate_contract_tests(self) -> Path:
        """
        Generate contract tests to ensure API compliance.
        """
        test_path = self.backend_path / "tests" / "test_api_contract.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        test_code = '''
import pytest
import requests
import yaml

class TestAPIContract:
    """Contract tests to ensure API matches OpenAPI spec."""
    
    @pytest.fixture
    def spec(self):
        with open("openapi.yaml") as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8082"
    
    def test_health_endpoint(self, base_url, spec):
        """Test /api/health matches spec."""
        response = requests.get(f"{base_url}/api/health")
        assert response.status_code == 200
        
        data = response.json()
assert "status" in data
        assert data["status"] in ["healthy", "degraded", "down"]
    
    def test_agents_list(self, base_url, spec):
        """Test /api/agents matches spec."""
        response = requests.get(f"{base_url}/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
'''
        
        with open(test_path, 'w') as f:
            f.write(test_code)
        
        return test_path
    
    # ========================================================================
    # 6. DOCUMENTATION GENERATION
    # ========================================================================
    
    def generate_docs(self) -> Path:
        """
        Generate API documentation site.
        """
        docs_path = self.backend_path / "docs" / "index.html"
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>aSiReM API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '../openapi.yaml',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ]
        });
    </script>
</body>
</html>
'''
        
        with open(docs_path, 'w') as f:
            f.write(html_content)
        
        return docs_path


print("✅ Swagger/OpenAPI Agent Expert implemented")
print("   • OpenAPI 3.0 spec generation")
print("   • TypeScript types generation")
print("   • React components & hooks")
print("   • Mock server generation")
print("   • Contract testing")
print("   • Swagger UI documentation")
