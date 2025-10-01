from json import dumps

import pytest
from pytest import raises

from asyncpraw.models import (
    Subreddit,
    SubredditWidgets,
    SubredditWidgetsModeration,
    Widget,
    WidgetModeration,
)
from asyncpraw.models.base import AsyncPRAWBase
from asyncpraw.models.reddit.widgets import WidgetEncoder

from ... import UnitTest


class TestSubredditWidgets(UnitTest):
    async def test_bad_attribute(self, reddit):
        subreddit = await reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with pytest.raises(AttributeError):
            _ = widgets.nonexistant_attribute

    def test_repr(self, reddit):
        widgets = SubredditWidgets(Subreddit(reddit, "fake_subreddit"))
        assert "SubredditWidgets(subreddit=Subreddit(display_name='fake_subreddit'))" == repr(widgets)

    def test_subreddit_widgets_mod(self, reddit):
        widgets = SubredditWidgets(Subreddit(reddit, "fake_subreddit"))
        assert isinstance(widgets.mod, SubredditWidgetsModeration)

    def test_widget_mod(self, reddit):
        w = Widget(reddit, {})
        assert isinstance(w.mod, WidgetModeration)
        assert w.mod.widget == w


class TestWidget(UnitTest):
    def test_equality(self):
        widget1 = Widget(None, {"id": "a"})
        widget2 = Widget(None, {"id": "b"})
        widget3 = Widget(None, {"id": "A"})
        assert widget1 == widget1
        assert widget1 != widget2
        assert widget1 == widget3

    def test_hash(self):
        widget1 = Widget(None, {"id": "a"})
        widget2 = Widget(None, {"id": "b"})
        widget3 = Widget(None, {"id": "A"})
        assert hash(widget1) == hash(widget1)
        assert hash(widget1) != hash(widget2)
        assert hash(widget1) == hash(widget3)


class TestWidgetEncoder(UnitTest):
    def test_bad_encode(self, reddit):
        data = [
            1,
            "two",
            SubredditWidgetsModeration(Subreddit(reddit, display_name="subreddit"), reddit),
        ]
        with raises(TypeError):
            dumps(data, cls=WidgetEncoder)  # should throw TypeError

    def test_good_encode(self, reddit):
        data = [
            1,
            "two",
            AsyncPRAWBase(reddit, _data={"_secret": "no", "3": 3}),
            Subreddit(reddit, "four"),
        ]
        assert dumps(data, cls=WidgetEncoder) == '[1, "two", {"3": 3}, "four"]'
