
import ast
import os

filename = '/Users/yacinebenhamou/aSiReM/sovereign-dashboard/real_agent_system.py'

class EndpointVisitor(ast.NodeVisitor):
    def __init__(self):
        self.endpoints = []
        self.handlers = {} # name -> node
        self.non_200_handlers = {} # name -> list of status codes

    def visit_FunctionDef(self, node):
        self.handlers[node.name] = node
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.handlers[node.name] = node
        self.generic_visit(node)

    def visit_Call(self, node):
        # Look for app.router.add_get/post/etc
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith('add_'):
            # It's likely a route definition
            # We assume the second arg is the handler
            if len(node.args) >= 2:
                path = node.args[0]
                handler = node.args[1]
                
                path_val = "unknown"
                if isinstance(path, ast.Constant):
                    path_val = path.value
                elif isinstance(path, ast.Str): # Python < 3.8
                    path_val = path.s
                
                handler_name = "unknown"
                if isinstance(handler, ast.Attribute):
                    handler_name = handler.attr
                elif isinstance(handler, ast.Name):
                    handler_name = handler.id
                
                self.endpoints.append({
                    'path': path_val,
                    'handler': handler_name,
                    'method': node.func.attr.replace('add_', '').upper()
                })
        
        self.generic_visit(node)

class StatusVisitor(ast.NodeVisitor):
    """Visits a handler function to find status=..."""
    def __init__(self):
        self.status_codes = []

    def visit_Call(self, node):
        # web.json_response(..., status=503)
        # web.Response(..., status=404)
        for keyword in node.keywords:
            if keyword.arg == 'status':
                if isinstance(keyword.value, ast.Constant):
                    self.status_codes.append(keyword.value.value)
                elif isinstance(keyword.value, ast.Num): # Python < 3.8
                    self.status_codes.append(keyword.value.n)
        self.generic_visit(node)

def analyze():
    with open(filename, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    visitor = EndpointVisitor()
    visitor.visit(tree)
    
    print(f"Total defined endpoints: {len(visitor.endpoints)}")
    
    non_200_count = 0
    endpoints_with_non_200 = []

    for ep in visitor.endpoints:
        handler_name = ep['handler']
        if handler_name in visitor.handlers:
            handler_node = visitor.handlers[handler_name]
            status_visitor = StatusVisitor()
            status_visitor.visit(handler_node)
            
            codes = [c for c in status_visitor.status_codes if c != 200]
            if codes:
                non_200_count += 1
                endpoints_with_non_200.append({
                    'path': ep['path'],
                    'method': ep['method'],
                    'handler': handler_name,
                    'codes': sorted(list(set(codes)))
                })
        else:
             print(f"Warning: Handler {handler_name} not found in parsed functions")

    print(f"\nEndpoints that explicitly return non-200 status codes: {non_200_count}")
    print("-" * 60)
    print(f"{'METHOD':<8} {'PATH':<40} {'CODES':<15} {'HANDLER'}")
    print("-" * 60)
    for ep in endpoints_with_non_200:
        codes_str = ", ".join(map(str, ep['codes']))
        print(f"{ep['method']:<8} {ep['path']:<40} {codes_str:<15} {ep['handler']}")

if __name__ == "__main__":
    analyze()
