"""Unit Tests for docker-pretty-ps

"""
import copy
from datetime import datetime, timedelta
import os

import dockerprettyps

from .data import docker_ps_data as test_ps_data
from .data.cli_args import CliArgs


class TestDockerPrettyPs(object):

    def test_version(self):
        """
        Tests dockerprettyps.version() method, basically making sure it doesnt crash.

        """
        assert dockerprettyps.__version__
        assert dockerprettyps.version()

    def test_clean_output(self):
        """
        Tests the dockerprettyps.clean_output() method to make sure it takes the standard out from a 'docker ps' command
        and properly translated that into a usable set of docker container data.

        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        data = open(os.path.join(dir_path, "data", "raw_docker_ps.txt"), "r").read()

        containers = dockerprettyps.clean_output(data)
        assert isinstance(containers, list)
        assert len(containers) == 16
        for container in containers:
            assert container.get("container_id")
            assert container.get("image")
            assert container.get("command")
            assert container.get("created")
            assert container.get("created_date")
            assert container.get("status")
            assert container.get("status_date")
            assert container.get("running")

    def test__parse_ports(self):
        """
        Tests the dockerprettyps._parse_ports() method ensure that we break apart ports properly as a trimmed list.

        """
        port_str = ' 0.0.0.0:5000->5000/tcp, 0.0.0.0:5001->80/tcp'
        ports = dockerprettyps._parse_ports(port_str)
        assert isinstance(ports, list)
        assert ports == ['0.0.0.0:5000->5000/tcp', '0.0.0.0:5001->80/tcp']

        port_str = ' '
        ports = dockerprettyps._parse_ports(port_str)
        assert isinstance(ports, list)
        assert ports == []
        # assert type(test_ps_data.ps_data_1) == str

    def test__parse_ps_date(self):
        """
        Tests the dockerprettyps._clean_ps_date() method to make sure it takes docker ps date differences and makes
        a real datetime.
        United
        Example input: Up 20 hours

        """
        status_date_str = 'Up 12 minutes'
        the_date_minutes = dockerprettyps._parse_ps_date(status_date_str)

        assert isinstance(the_date_minutes, datetime)
        assert the_date_minutes < datetime.now()
        assert the_date_minutes > datetime.now() - timedelta(minutes=13)

        create_date_str = '5 days ago'
        the_date_days = dockerprettyps._parse_ps_date(create_date_str)

        assert isinstance(the_date_days, datetime)
        assert the_date_days < datetime.now()
        assert the_date_days > datetime.now() - timedelta(days=6)

    def test__clean_status(self):
        """
        Tests the dockerprettyps._clean_status() method to see if a the output from a container signifies if the
        container is running currently.

        """
        assert not dockerprettyps._clean_status("Exited (1) 22 minutes ago")
        assert dockerprettyps._clean_status("Up 12 minutes")

    def test_get_container_colors(self):
        """
        Tests the dockerprettyps.get_container_colors() method which runs all containers throuh the get_color method(),
        to try and assign a semi unique color to an instance based on it's container name.

        """
        containers = test_ps_data.ps_containers
        colorless_containers = []
        for c in containers:
            c.pop('color')
            colorless_containers.append(c)

        color_containers = dockerprettyps.get_container_colors(colorless_containers)
        for c in color_containers:
            assert 'color' in c
            assert isinstance(c['color'], str)

    def test_get_color(self):
        """
        Tests the dockerprettyps.get_color() method to make sure any int passed will return an ANSII color code.

        """
        assert dockerprettyps.get_color(1) == "\033[94m"
        assert dockerprettyps.get_color(200) == "\033[92m"

    def test__get_num_running_containers(self):
        """
        Tests the dockerprettyps._get_num_running_containers() method to make sure it can actually count.

        """
        assert dockerprettyps._get_num_running_containers(test_ps_data.ps_containers) == 5

    def test_filter_containers(self):
        """
        Tests the dockerprettyps.filter_containers() method to make sure it removes containers based on 'search' as well
        as running or not running containers.

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
        Tests the dockerprettyps.order_containers() method to make sure we order containers as you would expect.

        """
        self.order_containers_standard()
        self.order_containers_reverse()
        self.order_containers_by_name()
        self.order_containers_by_create_date()

    def order_containers_standard(self):
        """
        Tests that dockerprettyps.order_containers() will order containers by status_date by default.
        The default will list containers by oldest status_date to newest.

        """
        ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, CliArgs())
        position_first_status_date = ordered[0]["status_date"]
        position_last_status_date = ordered[len(ordered) - 1]["status_date"]

        assert isinstance(ordered, list)
        assert position_first_status_date < position_last_status_date

    def order_containers_reverse(self):
        """
        Tests that dockerprettyps.order_containers() will order containers by status_date by default.
        This will list containers by newest status_date to oldest.
        """
        args = CliArgs()
        args.reverse = True
        ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
        position_first_date = ordered[0]["status_date"]
        position_last_date = ordered[len(ordered) - 1]["status_date"]
        assert position_first_date > position_last_date

    def order_containers_by_create_date(self):
        """
        Tests that dockerprettyps.order_containers() will order containers by created date.

        """
        args = CliArgs()
        phrases = ["created", "created"]
        for phrase in phrases:
            args.order = phrase
            args.reverse = False
            ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
            position_first_date = ordered[0]["created_date"]
            position_last_date = ordered[len(ordered) - 1]["created_date"]
            assert position_first_date < position_last_date

            args.reverse = True
            reverse_order = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
            position_first_date = reverse_order[0]["created_date"]
            position_last_date = reverse_order[len(ordered) - 1]["created_date"]
            assert position_first_date > position_last_date

    def order_containers_by_name(self):
        """
        Tests that dockerprettyps.order_containers() will order containers by name.

        """
        args = CliArgs()
        phrases = ["name", "container"]
        for phrase in phrases:
            args.order = phrase
            ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
            position_first_name = ordered[0]["name"]
            position_last_name = ordered[len(ordered) - 1]["name"]
            assert position_first_name == "alpine-sshd"
            assert position_last_name == "some-postgres"

    def order_containers_by_image(self):
        """
        Tests that dockerprettyps.order_containers() will order containers by name.

        """
        args = CliArgs()
        phrases = ["name", "container"]
        for phrase in phrases:
            args.order = phrase
            ordered = dockerprettyps.order_containers(test_ps_data.ps_containers, args)
            position_first_name = ordered[0]["name"]
            position_last_name = ordered[len(ordered) - 1]["name"]
            assert position_first_name == "alpine-sshd"
            assert position_last_name == "some-postgres"

    def test_print_format(self):
        """
        Tests the dockerprettyps.print_format() method, primarily checking that the method doesnt fail, since it mostly
        just prints to the console.

        """
        assert dockerprettyps.print_format(test_ps_data.ps_containers, 6, 5, CliArgs())

    def test_container_display_name(self):
        """
        Tests the dockerprettyps.container_display_name() method to see if we create the right console formatting for a
        container, with potential bolding to highlight search items.

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
        Tests the dockerprettyps._handle_column_state() method, to make sure we convert the shell output to a state that
        we can control and use.

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
        Tests the dockerprettyps._handle_column_status() method, to make sure we convert the shell output to a status
        that we can control and use.

        """
        containers = test_ps_data.ps_containers
        for container in containers:
            if container["name"] == "some-postgres":
                test_container = container

        args = CliArgs()
        args.all = True
        selected_args = ["s"]
        assert dockerprettyps._handle_column_status(test_container, selected_args, args) == \
            [['\x1b[1m\tStatus:\x1b[0m', 'Up 3 weeks']]

    def test__handle_column_ports(self):
        """
        Tests the dockerprettyps._handle_column_ports() method, to make sure we convert the shell output to ports that
        we can control and use.

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
        Tests the dockerprettyps._handle_column_created() method, to make sure we convert the shell output to a format
        that we can control and use.

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

    # def test_print_data(self):
    #     dockerprettyps.print_data

    def test_give_json(self):
        """
        Tests the dockerprettyps.give_json() method, making sure we output the same data we would normally, but in JSON.

        """
        containers = copy.deepcopy(test_ps_data.ps_containers)
        the_json = dockerprettyps.give_json(containers, CliArgs())
        assert the_json

    def test__json_container_dates(self):
        """
        Tests the dockerprettyps._json_container_dates() method, to ensure that we convert python datetimes to json
        friendly time stamps.

        """
        containers = test_ps_data.ps_containers
        json_dated_containers = dockerprettyps._json_container_dates(containers)
        for container in json_dated_containers:
            assert isinstance(container["status_date"], str)

# End File docker-pretty-ps/tests/test_dockerprettyps.py
