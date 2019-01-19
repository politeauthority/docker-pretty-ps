from datetime import datetime

ps_containers = [
    {
        'container_id': '1a31fcaccf59',
        'image_id': 'badactorservices_bad-actor-services',
        'command': "/bin/sh -c 'gunicor…",
        'created': '4 days ago',
        'status': 'Up 4 days',
        'status_date': datetime(2019, 1, 15, 3, 6, 40, 586865),
        'running': True,
        'ports': ['80/tcp'],
        'name': 'badactorservices_bad-actor-services_1',
        'color': '\x1b[95m'
    },
    {
        'container_id': 'd55ab151ce26',
        'image_id': 'badactorservices_bad-actor-services-data',
        'command': 'tail -f /dev/null',
        'created': '4 days ago',
        'status': 'Up 4 days',
        'status_date': datetime(2019, 1, 15, 3, 6, 40, 586889),
        'running': True,
        'ports': [],
        'name': 'badactorservices_bad-actor-services-data_1',
        'color': '\x1b[94m'
    },
    {
        'container_id': 'd4129f2a0d3b',
        'image_id': 'jwilder/nginx-proxy',
        'command': '/app/docker-entrypo…',
        'created': '4 days ago',
        'status': 'Up 4 days',
        'status_date': datetime(2019, 1, 15, 3, 6, 40, 586903),
        'running': True,
        'ports': ['0.0.0.0:80->80/tcp', '0.0.0.0:443->443/tcp'],
        'name': 'nginx-proxy',
        'color': '\x1b[92m'
    },
    {
        'container_id': '42df45bdc8b3',
        'image_id': 'postgres:alpine',
        'command': 'docker-entrypoint.s…',
        'created': '5 months ago',
        'status': 'Up 3 weeks',
        'status_date': datetime(2019, 1, 19, 3, 6, 40, 586918),
        'running': True,
        'ports': ['10.138.44.203:5432->5432/tcp'],
        'name': 'some-postgres',
        'color': '\x1b[91m'
    },
    {
        'container_id': '23a8d9762781',
        'image_id': 'danielguerra/alpine-sshd',
        'command': 'docker-entrypoint.s…',
        'created': '6 months ago',
        'status': 'Up 4 months',
        'status_date': datetime(2019, 1, 19, 3, 6, 40, 586931),
        'running': True,
        'ports': ['0.0.0.0:4848->22/tcp'],
        'name': 'alpine-sshd',
        'color': '\x1b[96m'
    },
    {
        'container_id': '25a8d92781',
        'image_id': 'danielguerra/alpine-sshd',
        'command': 'docker-entrypoint.s…',
        'created': '6 months ago',
        'status': 'Up 5 months',
        'status_date': datetime(2019, 1, 19, 3, 6, 40, 586931),
        'running': False,
        'ports': ['0.0.0.0:4849->22/tcp'],
        'name': 'alpine-sshd2',
        'color': '\x1b[96m'
    }
]
