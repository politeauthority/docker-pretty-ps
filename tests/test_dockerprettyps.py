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
        assert dockerprettyps.print_format(test_ps_data.ps_containers, 6, 5, CliArgs())

# End File docker-pretty-ps/tests/test_dockerprettyps.py
