import ast
from contextlib import contextmanager


def add_scope_context(node):
    """Provide to scope context to all nodes"""
    return ScopeTransformer().visit(node)


class ScopeMixin(object):
    """
    Adds a scope property with the current scope (function, module, for loop)
    a node is part of.
    """
    scopes = []

    @contextmanager
    def enter_scope(self, node):
        if self._is_scopable_node(node):
            self.scopes.append(node)
            yield
            self.scopes.pop()
        else:
            yield

    @property
    def scope(self):
        try:
            return self.scopes[-1]
        except IndexError:
            return None

    def _is_scopable_node(self, node):
        scopes = [ast.Module, ast.FunctionDef, ast.For, ast.If, ast.With]
        return len([s for s in scopes if isinstance(node, s)]) > 0


class ScopeList(list):
    def find(self, lookup):
        for scope in reversed(self):
            for var in scope.vars:
                if (isinstance(var, ast.alias) and var.name == lookup) or \
                   (var.id == lookup):
                    return var

    def find_import(self, lookup):
        for scope in reversed(self):
            if hasattr(scope, "imports"):
                for imp in scope.imports:
                    if imp.name == lookup:
                        return imp


class ScopeTransformer(ast.NodeTransformer, ScopeMixin):
    """
    Adds a scope attribute to each node.
    The scope contains the current scope (function, module, for loop)
    a node is part of.
    """

    def visit(self, node):
        with self.enter_scope(node):
            node.scopes = ScopeList(self.scopes)
            return super(ScopeTransformer, self).visit(node)
