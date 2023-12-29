from Rule.rule import rule
from User.user import user as vpn_user
from core import Body as vpn_body


class regulation_VLAN(rule):
    def __init__(self, name, ip, port, id_vlan):
        super().__init__(name, 0, ip, port, id_vlan)
        self._id_vlan = id_vlan

    def check(self, user: vpn_user, body: vpn_body) -> bool:
        dest_ip = '127.0.0.1' if body.dest_ip == 'localhost' else body.dest_ip
        return user.id_vlan != self._id_vlan or dest_ip != self.ip or self.port != body.dest_port

    def dict_to_rule(dict):
        parsed_rule = to_VLAN(dict['name'], dict['ip'], dict['port'], dict['e_id'])
        return parsed_rule


class regulation_User(rule):
    def __init__(self, name, ip, port, user_id):
        super().__init__(name, 1, ip, port, user_id)
        self._user_id = user_id

    def check(self, user: vpn_user, body: vpn_body) -> bool:
        dest_ip = '127.0.0.1' if body.dest_ip == 'localhost' else body.dest_ip
        return user.id != self._user_id or dest_ip != self.ip or self.port != body.dest_port

    def dict_to_rule(dict):
        parsed_rule = to_User(dict['name'], dict['ip'], dict['port'], dict['e_id'])
        return parsed_rule