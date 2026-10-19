from channels.generic.websocket import AsyncJsonWebsocketConsumer


class IrrigationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return
        org_id = self.scope.get("organization_id")
        if not org_id:
            await self.close()
            return
        self.group = f"org_{org_id}_irrigation"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        group = getattr(self, "group", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def irrigation_event(self, event):
        await self.send_json(event.get("payload") or {})
