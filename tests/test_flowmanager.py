import unittest

from knosk.core import Flow


class FlowManagerTest(unittest.TestCase):

    def test_simple_routing(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return payload, ctx
        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_two_handlers(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return payload, ctx

        @f.renderer("test")
        def r(flow, render_name, payload, ctx):
            return "render"

        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_calling_next_render(self):
        f = Flow()

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            return flow.render("somerender", payload, ctx)

        @f.renderer("somerender")
        def r(flow, render_name, payload, ctx):
            return "render"

        r = f.handle("test", {"a": "a"})

        assert r == "render"

    def test_simple_routing_with_positive_conditions(self):
        f = Flow()

        def condition(flow, parent, payload, ctx):
            return None

        @f.handler("test", conditions=[condition])
        def h(flow, render_name, payload, ctx):
            return payload, ctx

        self.assertEqual(f.handle("test", {"a": "a"}, {}), ({"a": "a"}, {}))

    def test_simple_routing_with_negative_conditions(self):
        f = Flow()

        def condition(flow, parent, payload, ctx):
            return f.render("condition", payload, ctx)

        @f.renderer("condition")
        def r(flow, render_name, payload, ctx):
            return "render"

        @f.handler("test", conditions=[condition])
        def h(flow, render_name, payload, ctx):
            return payload, ctx

        r = f.handle("test", {"a": "a"})

        self.assertEqual(r, "render")

    def test_fallback(self):
        def a(ex, route_name, payload, ctx):
            self.assertEqual(route_name, "test")

        f = Flow(a)

        @f.handler("test")
        def h(flow, render_name, payload, ctx):
            raise Exception()

        f.handle("test", {"a": "a"})
