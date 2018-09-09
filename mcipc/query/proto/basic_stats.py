"""Basic statistics protocol."""

from ipaddress import IPv4Address
from typing import NamedTuple

from mcipc.query.proto.common import MAGIC, random_session_id, Type


__all__ = ['Request', 'BasicStats']


class Request(NamedTuple):
    """Basic statistics request packet."""

    magic: bytes
    type: Type
    session_id: int
    challenge_token: int

    def __bytes__(self):
        """Returns the packet as bytes."""
        payload = self.magic
        payload += bytes(self.type)
        payload += self.session_id.to_bytes(4, 'big')
        payload += self.challenge_token.to_bytes(4, 'big')
        return payload

    @classmethod
    def create(cls, challenge_token, session_id=None):
        """Creates a new request with the specified challenge
        token and the specified or a random session ID.
        """
        if session_id is None:
            session_id = random_session_id()

        return cls(MAGIC, Type.STAT, session_id, challenge_token)


class BasicStats(NamedTuple):
    """Basic statistics response packet."""

    type: Type
    session_id: int
    motd: str
    game_type: str
    map: str
    num_players: int
    max_players: int
    host_port: int
    host_ip: IPv4Address

    @classmethod
    def from_bytes(cls, bytes_):
        """Creates the packet from the respective bytes."""
        type_ = int.from_bytes(bytes_[0:1], 'big')
        session_id = int.from_bytes(bytes_[1:5], 'big')

        try:
            *blocks, port_ip, _ = bytes_[5:].split(b'\0')
        except ValueError:
            raise ValueError('Unexpected amount of Null terminated strings.')

        strings = [block.decode() for block in blocks]

        try:
            motd, game_type, map_, num_players, max_players = strings
        except ValueError:
            raise ValueError('Unexpected amount of string fields.')

        num_players = int(num_players)
        max_players = int(max_players)
        host_port = int.from_bytes(port_ip[0:2], 'little')
        host_ip = IPv4Address(port_ip[2:].decode())
        return cls(
            type_, session_id, motd, game_type, map_, num_players, max_players,
            host_port, host_ip)
