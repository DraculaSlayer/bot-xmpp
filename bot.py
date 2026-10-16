import logging
import d20
import os
from dotenv import load_dotenv

import asyncio
import slixmpp


class MUCBot(slixmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)

        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)

    async def start(self, event):
        await self.get_roster()
        self.send_presence()
        self.plugin["xep_0045"].join_muc(
            self.room,
            self.nick,
        )

    def muc_message(self, msg):
        if msg["body"].startswith("!"):
            result = d20.roll(msg["body"].replace("!", ""))
            self.send_message(
                mto=msg["from"].bare, mbody=str(result), mtype="groupchat"
            )

    def muc_online(self, presence):
        if presence["muc"]["nick"] != self.nick:
            self.send_message(
                mto=presence["from"].bare,
                mbody="Hola putos de mierda, %s %s"
                % (presence["muc"]["role"], presence["muc"]["nick"]),
                mtype="groupchat",
            )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-8s %(message)s", filename="bot.log"
    )

    load_dotenv()

    user = os.getenv("USER")
    passwd = os.getenv("PASS")
    group = os.getenv("GROUP")
    nick = os.getenv("NICK")

    xmpp = MUCBot(user, passwd, group, nick)
    xmpp.register_plugin("xep_0030")  # Service Discovery
    xmpp.register_plugin("xep_0045")  # Multi-User Chat
    xmpp.register_plugin("xep_0199")  # XMPP Ping

    xmpp.connect()
    asyncio.get_event_loop().run_forever()
