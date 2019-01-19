#!/usr/bin/env python
"""docker-pretty-ps
Tired of that awful super wide docker ps output? Try docker-pretty-ps!

Invoke by calling docker-pretty-ps and get an output like so,

pa@host:~/$ docker-pretty-ps
All currently running docker containers

bad-actor-services_bad-actor-services-data_1
    Status:               Up About an hour
    Ports:
    Created:              4 days ago
    Container ID:         815409a7e562
    Image ID:             bad-actor-services_bad-actor-services-data
    Command:              tail -f /dev/null

bad-actor-services_bad-actor-services-web_1
    Status:               Up About an hour
    Ports:                0.0.0.0:5000->5000/tcp
                          0.0.0.0:5001->80/tcp
    Created:              4 days ago
    Container ID:         cc74d0f53d11
    Image ID:             bad-actor-services_bad-actor-services-web
    Command:              tail -f /dev/null

Total containers:   9
Total running:      2

"""
import argparse
from datetime import datetime, timedelta
import json
from operator import itemgetter
import subprocess

from dockerprettyps import errors

__version__ = "0.0.1a75"
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
    Primary start of the CLI application

    """
    args = _parsed_args()

    if args.version:
        version()

    try:
        raw_containers = get_raw_containers()
    except errors.BadResponseDockerEngine:
        print("%sError:%s Bad response from the Docker Engine" % (RED, ENDC))
        exit(1)

    containers = clean_output(raw_containers)
    total_containers = len(containers)
    total_running_containers = _get_num_running_containers(containers)
    containers = filter_containers(containers, args)
    containers = order_containers(containers, args)

    if args.json:
        give_json(containers, args)
    else:
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
        "-j",
        "--json",
        default="",
        action='store_true',
        help="Instead of printing, creates a json response of the container data.")
    parser.add_argument(
        "-v",
        "--version",
        default=False,
        action='store_true',
        help="Reverses the display order.")

    args = parser.parse_args()

    # Parse includes
    includes = []
    if args.include:
        for letter in args.include:
            includes.append(letter)
        args.include = includes

    # Parse searches
    if ',' in args.search:
        searches = args.search.split(',')
    elif args.search == "":
        searches = []
    else:
        searches = [args.search]
    args.search = searches

    return args


def version():
    """
    Displays docker-pretty-ps version to the cli.

    """
    print(__title__)
    print("\t%sdocker-pretty-ps%s                                Version: %s" % (BOLD, ENDC, __version__))
    print("                                                        @politeauthority\n\n")
    print("                                                        https://github.com/politeauthority/docker-pretty-ps\n\n")
    exit()


def get_raw_containers():
    """
    Runs the shell command to get the container all data from Docker.

    :returns: The raw information from the `docker ps` command.
    :rtype: str
    """
    cmds = ["docker", "ps", "-a"]
    out = subprocess.Popen(
        cmds,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    stdout = stdout.decode("utf-8")
    if "Error" in stdout or "Cannot connect" in stdout:
        raise errors.BadResponseDockerEngine

    return stdout


def clean_output(output):
    """
    Cleans the output from the docker ps command, storing it into a list of dicts.

    :param output: The standard out from the docker ps command.
    :type output: str
    :returns: Cleaned, usable output from docker-ps
    :rtype: list
    """
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
    Cleans port data from docker ps.

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
    Sets an ANSII color cmd to use for each container based on it's position in the list.

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

    :param count: The container number, 0 indexed.
    :type count: int
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
    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :returns: The filtered list of dicts of containers.
    :rtype: list
    """
    if not args.search and args.all:
        return containers

    # Filter containers by search criteria.
    filtered_containers = []
    if args.search:
        for container in containers:
            for search in args.search:
                if search in container['name']:
                    filtered_containers.append(container)
                    break
    else:
        filtered_containers = containers

    # Filter only running containers.
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
    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
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
        if not args.all:
            print('Currently running containers with: "%s" \n' % '", "'.join(args.search))
        else:
            print('All cotnainers containers with: "%s" \n' % '", "'.join(args.search))
    else:
        if not args.all:
            print("All currently running docker containers\n")
        else:
            print("All docker containers\n")

    pretty_print_fmt_containers(containers, args)

    print("\nTotal containers:\t%s" % total_containers)
    print("Total running:\t\t%s" % total_running_containers)
    if args.search:
        print("Containers in search:\t%s" % len(containers))

    return True


def pretty_print_fmt_containers(containers, args):
    """
    Pretty print container data in regular long form, displaying all data.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param args: Parsed arguments from cli.
    :type args: <Namespace> obj
    """
    selected_includes = ["r", "s", "c", "p", "n", "i", "m"]
    if args.slim or args.include:
        selected_includes = []

    if args.include:
        for include in args.include:
            selected_includes.append(include)

    print_content = {}
    for container in containers:
        container_content = {
            "display_name": container_display_name(args, container),
            "data": []
        }

        # Prep the container Co(n)tainer ID
        if "n" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tContainer ID:" + ENDC,
                    container["container_id"]])

        # Prep the container (i)mage ID
        if "i" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tImage ID:" + ENDC,
                    container["image_id"]])

        # Prep the container co(m)mand
        if "m" in selected_includes:
            container_content["data"].append(
                [
                    BOLD + "\tCommand:" + ENDC,
                    container["command"]])

        # Prep the container (c)reated
        created_data = _handle_column_created(args, container, selected_includes)
        if created_data:
            container_content["data"] += created_data

        # Prep the container (s)tatus
        status_data = _handle_column_status(args, container, selected_includes)
        if status_data:
            container_content["data"] += status_data

        # Prep the container state (r)
        state_data = _handle_column_state(args, container, selected_includes)
        if state_data:
            container_content["data"] += state_data

        # Prep the container (p)orts
        ports_data = _handle_column_ports(args, container, selected_includes)
        if ports_data:
            container_content["data"] += ports_data

        print_content[container["name"]] = container_content

    print_data(print_content)

    return True


def container_display_name(args, container):
    """
    Creates the container display name with formatting and colors.

    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    :param container: The container to have information formatted for print.
    :type container: dict
    :returns: The container's display name with color and formatting.
    :rtype: str
    """
    if not args.search:
        return container["color"] + container["name"] + ENDC
    else:
        highlighted_name = container["color"] + container["name"]

        for search in args.search:
            highlighted_name = highlighted_name.replace(
                search,
                BOLD + container["color"] + search + ENDC + container["color"])

        return highlighted_name + ENDC


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
    Handles the selecting of the status (s) data for a container.

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

        col_width = 30
        for row in container["data"]:
            if len(row[0]) == 0:
                print("                              %s" % row[1])
            else:
                print("%s %s" % (row[0].ljust(col_width), row[1]))
        print("")


def give_json(containers, args):
    """
    This thing is supposed to give pretty output, but maybe someone... somewhere just needs JSON. Well here we go!
    Here we will give JSON over standard out when the -j arg is supplied.

    :param containers: The containers found from docker ps.
    :type containers: list
    :param args: The CLI args
    :type args: <class 'argparse.Namespace'>
    """
    clean_date_containers = _json_container_dates(containers)
    ret_dict = {
        "total_containers": len(containers),
        "objects": clean_date_containers
    }
    print(json.dumps(ret_dict, indent=4, sort_keys=True))
    # print(json.dumps(ret_dict))


def _json_container_dates(containers):
    """
    Moves container "status date" to a JSON friendly value.

    :param containers: The containers found from docker ps.
    :type containers: list
    :returns: The containers found from docker ps, with JSON friedly dates.
    :rtype: list
    """
    clean_containers = []
    for container in containers:
        tmp_container = container
        tmp_container["status_date"] = str(tmp_container["status_date"])
        clean_containers.append(tmp_container)

    return clean_containers


if __name__ == "__main__":
    run_cli()
