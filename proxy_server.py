import nginx
from dotenv import load_dotenv
import os

from config import SSL_DHPARAM, SSL_CERTIFICATE, SSL_CERTIFICATE_KEY

load_dotenv()


def create_config(listen_port: int, proxy_port: int) -> nginx.Conf:
    config = nginx.Conf()
    map = nginx.Map('$http_upgrade $connection_upgrade',
                    nginx.Key('default', 'upgrade'),
                    nginx.Key("''", 'close'))
    server = nginx.Server()
    server.add(nginx.Key('server_name', 'game.tondurakgame.com'),
               nginx.Key('listen', f'{listen_port} ssl'),
               nginx.Key('proxy_http_version', '1.1'),
               nginx.Key('proxy_set_header', 'Upgrade $http_upgrade'),
               nginx.Key('proxy_set_header', 'Connection $connection_upgrade'),
               nginx.Key('proxy_set_header', 'Host $host'),

               nginx.Key('ssl_certificate', SSL_CERTIFICATE),
               nginx.Key('ssl_certificate_key', SSL_CERTIFICATE_KEY),
               nginx.Key('ssl_dhparam', SSL_DHPARAM),

               nginx.Key('ssl_session_cache', 'shared:le_nginx_SSL:10m'),
               nginx.Key('ssl_session_timeout', '1440m'),
               nginx.Key('ssl_session_tickets', 'off'),
               nginx.Key('ssl_protocols', 'TLSv1.2 TLSv1.3'),
               nginx.Key('ssl_prefer_server_ciphers', 'off'),
               nginx.Key('ssl_ciphers',
                         '"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"'),
               nginx.Location('/', nginx.Key('proxy_pass', f'http://localhost:{proxy_port}')))
    config.add(map)
    config.add(server)
    return config
