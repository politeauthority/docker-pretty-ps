"""Unit Tests for docker-pretty-ps

"""
from datetime import datetime

import dockerprettyps

from .data import docker_ps as test_ps_data
from .data.cli_args import CliArgs


class TestDockerPrettyPs(object):

    def test__clean_ports(self):
        """

        """
        port_str = ' 0.0.0.0:5000->5000/tcp, 0.0.0.0:5001->80/tcp'
        ports = dockerprettyps._clean_ports(port_str)
        assert ports == ['0.0.0.0:5000->5000/tcp', '0.0.0.0:5001->80/tcp']
        # assert type(test_ps_data.ps_data_1) == str

    def test__clean_status_date(self):
        """

        """
        date_str = 'Up 12 minutes'
        the_date = dockerprettyps._clean_status_date(date_str)
        # import pdb; pdb.set_trace()

        # assert ports == ['0.0.0.0:5000->5000/tcp', '0.0.0.0:5001->80/tcp']
        assert isinstance(the_date, datetime)

    def test__clean_status(self):
        """

        """
        assert not dockerprettyps._clean_status("Exited (1) 22 minutes ago")
        assert dockerprettyps._clean_status("Up 12 minutes")

    def test_get_container_colors(self):
        """

        """
        colorless_containers = []
        for c in test_ps_data.ps_containers:
            c.pop('color')
            colorless_containers.append(c)

        color_containers = dockerprettyps.get_container_colors(colorless_containers)
        for c in color_containers:
            assert 'color' in c
            assert isinstance(c['color'], str)

    def test_get_color(self):
        """

        """
        assert dockerprettyps.get_color(1) == "\033[94m"
        assert dockerprettyps.get_color(200) == "\033[92m"

    def test__get_num_running_containers(self):
        """

        """
        assert dockerprettyps._get_num_running_containers(test_ps_data.ps_containers) == 5

    def test_filter_containers(self):
        """

        """
        assert len(test_ps_data.ps_containers) == 6

        filtered = dockerprettyps.filter_containers(test_ps_data.ps_containers, CliArgs())
        # assert len(filtered) == 5

        args = CliArgs()
        args.search = ["postgres"]
        filtered = dockerprettyps.filter_containers(test_ps_data.ps_containers, args)
        assert len(filtered) == 1

        args = CliArgs()
        args.search = ["postgres", "bad"]
        filtered = dockerprettyps.filter_containers(test_ps_data.ps_containers, args)
        assert len(filtered) == 3

        args = CliArgs()
        args.all = True
        filtered = dockerprettyps.filter_containers(test_ps_data.ps_containers, args)
        assert len(filtered) == 6

    def test_order_containers(self):
        """

        """
        ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, CliArgs())
        position_first_date = ordered[0]["status_date"]
        position_last_date = ordered[len(ordered) - 1]["status_date"]
        assert position_first_date > position_last_date

        # args = CliArgs()
        # args.reverse = True
        # ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
        # position_first_date = ordered[0]["status_date"]
        # position_last_date = ordered[len(ordered) - 1]["status_date"]
        # assert position_first_date < position_last_date

    def test_print_format(self):
        """

        """
        assert dockerprettyps.print_format(test_ps_data.ps_containers, 6, 5, CliArgs())

    def test_container_display_name(self):
        """

        """
        containers = test_ps_data.ps_containers
        container = containers[0]
        container_display = dockerprettyps.container_display_name(container, CliArgs())
        assert container_display == container["color"] + container["name"] + dockerprettyps.ENDC

        # Test that we bold the portion of a container name that matches a search if we have one.
        args = CliArgs()
        args.search = ["post"]
        for container in containers:
            if container["name"] == "some-postgres":
                assert dockerprettyps.container_display_name(container, args) == \
                    "\x1b[91msome-\x1b[1m\x1b[91mpost\x1b[0m\x1b[91mgres\x1b[0m"

    def test__handle_column_state(self):
        """

        """
        containers = test_ps_data.ps_containers
        for container in containers:
            if container["name"] == "some-postgres":
                test_container_on = container
            if container["name"] == "alpine-sshd2":
                test_container_off = container

        args = CliArgs()
        args.all = True
        selected_args = ["r", "s", "c", "p", "n", "i", "m"]
        assert dockerprettyps._handle_column_state(test_container_on, selected_args, args) == \
            [['\x1b[1m\tState:\x1b[0m', '\x1b[92m[ON]\x1b[0m']]

        assert dockerprettyps._handle_column_state(test_container_off, selected_args, args) == \
            [['\x1b[1m\tState:\x1b[0m', '\x1b[91m[OFF]\x1b[0m']]

    def test__handle_column_status(self):
        """

        """
        containers = test_ps_data.ps_containers
        for container in containers:
            if container["name"] == "some-postgres":
                test_container = container

        args = CliArgs()
        args.all = True
        selected_args = ["s"]
        # import pdb; pdb.set_trace()
        assert dockerprettyps._handle_column_status(test_container, selected_args, args) == \
            [['\x1b[1m\tStatus:\x1b[0m', 'Up 3 weeks']]

    def test__handle_column_ports(self):
        """

        """
        containers = test_ps_data.ps_containers
        for container in containers:
            if container["name"] == "some-postgres":
                test_container = container

        args = CliArgs()
        args.all = True
        selected_args = ["p"]

        assert dockerprettyps._handle_column_ports(args, test_container, selected_args) == \
            [['\x1b[1m\tPorts:\x1b[0m', '10.138.44.203:5432->5432/tcp']]

    def test__handle_column_created(self):
        """

        """
        containers = test_ps_data.ps_containers
        for container in containers:
            if container["name"] == "some-postgres":
                test_container = container

        args = CliArgs()
        args.all = True
        selected_args = ["c"]

        assert dockerprettyps._handle_column_created(args, test_container, selected_args) == \
            [['\x1b[1m\tCreated:\x1b[0m', '5 months ago']]

    def test_give_json(self):
        """

        """
        containers = test_ps_data.ps_containers
        assert dockerprettyps.give_json(containers, CliArgs())

    def test__json_container_dates(self):
        """

        """
        containers = test_ps_data.ps_containers
        json_dated_containers = dockerprettyps._json_container_dates(containers)
        for container in json_dated_containers:
            assert isinstance(container["status_date"], str)

# End File docker-pretty-ps/tests/test_dockerprettyps.py
