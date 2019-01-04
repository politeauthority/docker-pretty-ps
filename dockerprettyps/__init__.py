#!/usr/bin/env python
"""docker-pretty-ps
Tired of that awful super wide docker ps output? Try docker-pretty-ps!

Invoke by calling docker-pretty-ps and get an output like so,

pa@host:~/$ docker-pretty-ps

Name:         cool-freaking-container
Container ID: 1a685dd9d351
Image ID:     28bbeb325405
Created:      9 days ago
Status:       Up 43 minutes
Command:      "tail -f /dev/null"

Name:         some-postgres
Container ID: 0370c73b4951
Image ID:     postgres:alpine
Created:      9 days ago
Status:       Up 43 minutes
Command:      "/bin/sh -c 'while t..."

"""
import argparse
from datetime import datetime, timedelta
from operator import itemgetter
import subprocess

__version__ = "0.0.1a6"
__title__ = """
     _         _                                _   _
  __| |___  __| |_____ _ _   ___   _ __ _ _ ___| |_| |_ _  _   ___   _ __ ___
 / _` / _ \/ _| / / -_) '_| |___| | '_ \ '_/ -_)  _|  _| || | |___| | '_ (_-<
 \__,_\___/\__|_\_\___|_|         | .__/_| \___|\__|\__|\_, |       | .__/__/
                                  |_|                   |__/        |_|
"""

ENDC = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'


def run_cli():
    """
    Primary start of the application

    """
    args = _parsed_args()

    # Print the Version
    if args.version:
        print(__title__)
        print("\t%sdocker-pretty-ps%s                                Version: %s\n\n" % (BOLD, ENDC, __version__))
        exit()

    raw_containers = get_raw_containers()
    containers = clean_output(raw_containers)
    total_containers = len(containers)
    total_running_containers = _get_num_running_containers(containers)
    containers = filter_containers(containers, args)
    containers = order_containers(containers, args)
    print_format(
        containers,
        total_containers,
        total_running_containers,
        args)


def _parsed_args():
    """
    Parses args from the cli with ArgumentParser

    :returns: Parsed arguments
    :rtype: <Namespace> obj
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "search",
        nargs='?',
        default='',
        help="Phrase to search containers, comma separate multiples.")

    parser.add_argument(
        "-a",
        "--all",
        default=False,
        action='store_true',
        help="Selects against all rnning and stopped containers")
    parser.add_argument(
        "-s",
        "--slim",
        default=False,
        action='store_true',
        help="Shows a slim minimal output.")
    parser.add_argument(
        "-i",
        "--include",
        default=[],
        help="Data points to add to display, (c)reated, (p)orts, (i)mage_id, co(m)mand")
    parser.add_argument(
        "-o",
        "--order",
        nargs='?',
        default='',
        help="Order by, defaults to container start, allows 'container', 'image'.")
    parser.add_argument(
        "-r",
        "--reverse",
        default=False,
        action='store_true',
        help="Reverses the display order.")
    parser.add_argument(
        "-v",
        "--version",
        default=False,
        action='store_true',
        help="Reverses the display order.")

    args = parser.parse_args()

    includes = []
    if args.include:
        for letter in args.include:
            includes.append(letter)
        args.include = includes

    return args


def get_raw_containers():
    """
    Runs the shell command to get the container all data from Docker.

    :returns: The raw information from the `docker ps` command.
    :rtype: list
    """
    cmds = ["docker", "ps", "-a"]
    out = subprocess.Popen(
        cmds,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    return stdout


def clean_output(output):
    """
    Cleans the output from the docker ps command, storing it into a list of dicts.

    :param output: The standard out from the docker ps command.
    :type output: str
    :returns: Cleaned, usable output from docker-ps
    :rtype: list
    """
    output = output.decode("utf-8")
    lines = output.split("\n")
    containers = []
    for line in lines[1:]:
        line_split = line.split("  ")
        revised_line_split = []
        if len(line_split) == 1:
            continue
        for piece in line_split:
            if piece and piece.strip() != "":
                revised_line_split.append(piece)
        container = {
            "container_id": revised_line_split[0].strip(),
            "image_id": revised_line_split[1].strip(),
            "command": revised_line_split[2].strip().replace('"', ""),
            "created": revised_line_split[3].strip(),
            "status": revised_line_split[4].strip(),
            "status_date": _clean_status_date(revised_line_split[4].strip()),
            "running": _clean_status(revised_line_split[4])
        }

        # Not all containers will have ports
        if len(revised_line_split) == 6:
            container["ports"] = []
            container["name"] = revised_line_split[5].strip()
        else:
            container["ports"] = _clean_ports(revised_line_split[5])
            container["name"] = revised_line_split[6].strip()
        containers.append(container)

    containers = get_container_colors(containers)
    return containers


def _clean_ports(port_str):
    """
    :param port_str: The string of ports from the docker ps output.
    :type port_str: str
    :returns: The ports broken into a list.
    :rtype: list
    """
    port_str = port_str.strip()
    if ", " not in port_str:
        return [port_str]

    ports = port_str.split(', ')
    return ports


def _clean_status_date(val):
    """
    Gets the relative time the container was created based on the string from the docker ps command.

    :param val: The string representation of when the container was started.
    :type val: str
    :returns: Rough datetime for when the continer was started.
    :rtype: <Datetime obj>
    """
    now = datetime.now()
    cleaned = val.replace('Up ', '').lower()
    # 'Restarting' containers will look like so "Restarting (1) 36 seconds ago"
    if 'restarting' in cleaned:
        cleaned = cleaned[cleaned.find(')') + 1:]

    cleaned = cleaned.replace('ago', '').strip()

    if '(healthy' in cleaned:
        cleaned = cleaned[:cleaned.find('(healthy')].strip()

    elif '(health' in cleaned:
        cleaned = cleaned[:cleaned.find(')' + 1)].strip()

    elif 'exited (' in cleaned:
        cleaned = cleaned[cleaned.find(')') + 1:].strip()

    if 'seconds' in cleaned:
        digit = cleaned.replace(' seconds', '')
        digit = int(digit)
        the_date = now - timedelta(seconds=digit)
    elif 'minutes' in cleaned:
        digit = cleaned.replace(' minutes', '')
        digit = int(digit)
        the_date = now - timedelta(minutes=digit)
    elif 'about an hour' in cleaned:
        digit = 1
        the_date = now - timedelta(hours=digit)
    elif 'hours' in cleaned:
        digit = cleaned.replace(' hours', '')
        digit = int(digit)
        the_date = now - timedelta(hours=digit)
    elif 'days' in cleaned:
        digit = cleaned.replace(' days', '')
        digit = int(digit)
        the_date = now - timedelta(days=digit)

    else:
        the_date = now

    return the_date


def _clean_status(val):
    """
    Checks the status column to see if a container is running or exited, and return the value.

    :param val: The container status column value.
    :type val: str
    :returns: Whether or not the container is running.
    :rtype: bool
    """
    val = val.lower().strip()
    if 'exited (' in val or 'created' == val:
        return False

    return True


def get_container_colors(containers):
    """
    Sets the ANSII color cmd to use for each container based on it's position in the list.

    :param containers: The containers found from docker ps.
    :type containers: list
    :returns: Added color cmd to each container.
    :rtype: list
    """
    count = 0
    for c in containers:
        c['color'] = get_color(count)
        count += 1
    return containers


def get_color(count):
    """
    Gets a color from the list of colors.
    @todo: Some more colors that are visable on light and dark screens would be nice.

    :param count:
    :type count:
    :returns: The ASNII color to use when printing to the terminal.
    :rtype: int
    """
    colors = [
        '\033[94m',  # purple
        GREEN,       # green
        RED,         # red
        '\033[96m',  # cyan
        '\033[93m',  # yellow
        '\033[95m',  # magenta
    ]
    while count > len(colors):
        colors += colors

    return colors[count - 1]


def _get_num_running_containers(containers):
    """
    Gets the total number of currently running docker containers.

    :param containers: The containers found from docker ps.
    :type containers: list
    :returns: The number of containers currently running.
    :rtype int:
    """
    total_running = 0
    for container in containers:
        if container['running']:
            total_running += 1
    return total_running


def filter_containers(containers, args):
    """
    Filters containers by the search phrase matching the container name in some way.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param searches: The search phrase to search container names.
    :type searches: str
    :returns: The filtered list of dicts of containers.
    :rtype: list
    """
    if not args.search and args.all:
        return containers

    if ',' in args.search:
        searches = args.search.split(',')
    else:
        searches = [args.search]

    filtered_containers = []
    for container in containers:
        for search in searches:
            if search in container['name']:
                filtered_containers.append(container)
                break

    more_filtered_containers = []
    if not args.all:
        for container in filtered_containers:
            if container['running']:
                more_filtered_containers.append(container)
    else:
        more_filtered_containers = filtered_containers

    return more_filtered_containers


def order_containers(containers, args):
    """
    Orders containers based on the field requested.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param args: Parsed arguments from cli.
    :type args: <Namespace> obj
    :returns: The ordered list of dicts of containers.
    :rtype: list
    """
    if not containers:
        return containers

    field = 'status_date'
    if args.order:
        if args.order in ['container', 'container-name', 'container-id']:
            field = 'container_id'
        if args.order in ['image', 'image-id', 'image-name']:
            field = 'image_id'

    ordered_containers = sorted(containers, key=itemgetter(field))

    if args.reverse:
        ordered_containers.reverse()

    if field in ['status_date'] and not args.reverse:
        ordered_containers.reverse()
    return ordered_containers


def print_format(containers, total_containers, total_running_containers, args):
    """
    Actually prints the stuff to the console.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param total_containers: Number of containers.
    :type total_containers: int
    :param total_running_containers: Number of total running containers.
    :type total_running_containers: int
    :param args: Parsed arguments from cli.
    :type args: <Namespace> obj
    """
    if args.search:
        print("Currently running containers with: %s\n" % args.search)
    else:
        if not args.all:
            print("All currently running docker containers\n")
        else:
            print("All docker containers\n")

    pretty_print_fmt(containers, args)

    print("\nTotal containers:\t%s" % total_containers)
    print("Total running:\t\t%s" % total_running_containers)
    if args.search:
        print("Containers in search:\t%s" % len(containers))

    return True


def pretty_print_fmt(containers, args):
    """
    Pretty print container data in regular long form, displaying all data.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param args: Parsed arguments from cli.
    :type args: <Namespace> obj
    """
    selected_includes = ["r", "s", "c", "p", "n", "i", "m"]
    if args.slim:
        selected_includes = []

    if args.include:
        for include in args.include:
            selected_includes.append(include)

    print_content = {}
    for container in containers:
        container_content = {
            "display_name": container['color'] + container["name"] + ENDC,
            "data": []
        }

        state_data = _handle_column_state(args, container, selected_includes)
        if state_data:
            container_content["data"] += state_data

        status_data = _handle_column_status(args, container, selected_includes)
        if status_data:
            container_content["data"] += status_data

        ports_data = _handle_column_ports(args, container, selected_includes)
        if ports_data:
            container_content["data"] += ports_data

        created_data = _handle_column_created(args, container, selected_includes)
        if created_data:
            container_content["data"] += created_data

        # # Prep the Co(n)tainer ID
        if "n" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tContainer ID:" + ENDC,
                    container["container_id"]])

        # # Prep the (i)mage ID
        if "i" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tImage ID:" + ENDC,
                    container["image_id"]])

        # # Prep the Co(m)mand
        if "m" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tCommand:" + ENDC,
                    container["command"]])

        print_content[container["name"]] = container_content

    print_data(print_content)

    return True


def _handle_column_state(args, container, selected_includes):
    """
    Handles the selecting of the state (r) data for a container.

    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :param container: The container to have information formatted for print.
    :type container: dict
    :param selected_includes: Includes to be selected for return.
    :type selected_includes: list
    :returns: The print values for created data.
    :rtype: list
    """
    print_d = []
    if args.all and "r" in selected_includes:
        if container["running"]:
            print_d.append([
                BOLD + "\tState:" + ENDC,
                GREEN + "[ON]" + ENDC])
        else:
            print_d.append([
                BOLD + "\tState:" + ENDC,
                RED + "[OFF]" + ENDC])

    return print_d


def _handle_column_status(args, container, selected_includes):
    """
    Handles the selecting of the state (r) data for a container.

    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :param container: The container to have information formatted for print.
    :type container: dict
    :param selected_includes: Includes to be selected for return.
    :type selected_includes: list
    :returns: The print values for created data.
    :rtype: list
    """
    print_d = []
    if "s" in selected_includes:
        print_d.append(
            [
                BOLD + "\tStatus:" + ENDC,
                container["status"]])

    return print_d


def _handle_column_ports(args, container, selected_includes):
    """
    Handles the selecting of the port (p) data for a container for printing.

    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :param container: The container to have information formatted for print.
    :type container: dict
    :param selected_includes: Includes to be selected for return.
    :type selected_includes: list
    :returns: The print values for created data.
    :rtype: list
    """
    print_d = []
    # Prep the (p)orts
    if "p" in selected_includes:
        if len(container["ports"]) == 0:
            print_d.append(
                [
                    BOLD + "\tPorts:" + ENDC,
                    ''])
        elif len(container["ports"]) == 1:
            print_d.append(
                [
                    BOLD + "\tPorts:" + ENDC,
                    container["ports"][0]])
        else:
            c = 0
            for container_port in container["ports"]:
                container_port = container_port.strip()
                if c == 0:
                    print_d.append(
                        [
                            BOLD + "\tPorts:" + ENDC,
                            container_port])
                else:
                    print_d.append(["", container_port])
                c += 1

    return print_d


def _handle_column_created(args, container, selected_includes):
    """
    Handles the selecting of the created (c) data for a container.

    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :param container: The container to have information formatted for print.
    :type container: dict
    :param selected_includes: Includes to be selected for return.
    :type selected_includes: list
    :returns: The print values for created data.
    :rtype: list
    """
    print_d = []
    if "c" in selected_includes:
        print_d.append(
            [
                BOLD + "\tCreated:" + ENDC,
                container["created"]])
    return print_d


def print_data(container_info):
    """
    Prints data evenly spaced in a table like format.

    :param container_info: A List of lists to be printed and spaces evenly.
    :type container_info: dict
    """
    for container_name, container in container_info.items():
        print(container["display_name"])
        if not container["data"]:
            continue
        col_width = max(len(cell) for row in container["data"] for cell in row) + 2  # padding

        for row in container["data"]:
            print("".join(cell.ljust(col_width) for cell in row))
        print("")


if __name__ == "__main__":
    run_cli()
