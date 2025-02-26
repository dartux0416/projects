def ip_to_int(ip):
    octets = map(int, ip.split('.'))
    return sum([octet << (8 * (3 - i)) for i, octet in enumerate(octets)])

def int_to_ip(int_val):
    return '.'.join(str((int_val >> (8 * i)) & 0xFF) for i in reversed(range(4)))

def get_broadcast_address(network_address, subnet_mask):
    network_int = ip_to_int(network_address)
    mask_int = ip_to_int(subnet_mask)
    # Calculate the broadcast address by OR-ing the network address with the bitwise NOT of the subnet mask,
    # then ensuring the result is within the bounds of a 32-bit number by AND-ing with 0xFFFFFFFF.
    broadcast_int = network_int | ~mask_int & 0xFFFFFFFF
    return int_to_ip(broadcast_int)

def get_network_address(ip, subnet_mask):
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(subnet_mask)
    # Calculate the network address by AND-ing the IP address with the subnet mask.
    network_int = ip_int & mask_int
    return int_to_ip(network_int)

def subnet_mask_from_prefix_length(prefix_length):
    # Generate a subnet mask as a 32-bit integer.
    # Start with a 32-bit number with all bits set to 1 (0xFFFFFFFF),
    mask_int = (0xFFFFFFFF >> (32 - prefix_length)) << (32 - prefix_length)
    return int_to_ip(mask_int)

def netmask_to_cidr(netmask):
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])

def parse_mask(input_mask):
    if '/' in input_mask:
        prefix_length = int(input_mask.strip('/'))
        return subnet_mask_from_prefix_length(prefix_length), prefix_length
    else:
        return input_mask, netmask_to_cidr(input_mask)

def calculate_subnets(base_network, base_mask, sizes):
    sizes.sort(reverse=True)      
    subnets = []
    current_base = ip_to_int(base_network)
    base_mask, _ = parse_mask(base_mask)
    subnet_number = 1

    for size in sizes:
        new_prefix_length = 32
        while 2 ** (32 - new_prefix_length) < size + 2:  # +2 for network and broadcast address
            new_prefix_length -= 1

        new_mask = subnet_mask_from_prefix_length(new_prefix_length)
        subnet_network = int_to_ip(current_base)
        subnets.append((f"Network {subnet_number}", subnet_network, new_mask, new_prefix_length))

        current_base += 2 ** (32 - new_prefix_length)
        subnet_number += 1

    return subnets

def main():
    base_network = input("Insert base network IP:  ")
    base_mask = input("Insert subnet mask:  ")
    sizes = [int(s) for s in input("Insert subnets sizes separated by ',': ").split(',')]

    parsed_mask, base_prefix_length = parse_mask(base_mask)
    subnets = calculate_subnets(base_network, parsed_mask, sizes)

    for subnet_number, network, mask, prefix_length in subnets:
        network_address = get_network_address(network, mask)
        broadcast_address = get_broadcast_address(network, mask)
        first_host = int_to_ip(ip_to_int(network_address) + 1)
        last_host = int_to_ip(ip_to_int(broadcast_address) - 1)
        print(f"{'-' * 70}")
        print(f"{subnet_number}: {network}/{prefix_length} (Netmask: {mask}, CIDR: /{prefix_length})\n"
              f"First useful host: {first_host}\n"
              f"Last useful host: {last_host}\n"
              f"Broadcast address: {broadcast_address}\n"
              f"{'-' * 70}")

if __name__ == '__main__':
    main()
