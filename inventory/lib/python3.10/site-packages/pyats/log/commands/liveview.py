from . import _liveview_internal


class LiveViewSIO(_liveview_internal.LiveViewSIO):

    async def disconnect_request(self, sid):
        await super().disconnect_request(sid)

    async def liveview(self, sid, message):
        await super().liveview(sid, message)

    async def connect(self, sid, environ):
        await super().connect(sid, environ)
