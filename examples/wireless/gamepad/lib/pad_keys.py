# Link keys for paired game pads, kept in a file on the board's filesystem so a pad pairs once.
#
# One line per pad: address, key and key type as hex and decimal, space separated. Delete the file,
# or a line of it, to forget a pad.
import btclassic

KEY_FILE = "/bt_link_keys.txt"


def load():
    """Put every stored key back into the stack. Returns the addresses loaded."""
    addresses = []
    try:
        with open(KEY_FILE) as f:
            for line in f:
                parts = line.split()
                if len(parts) != 3:
                    continue
                address = bytes.fromhex(parts[0])
                btclassic.add_link_key(address, bytes.fromhex(parts[1]), int(parts[2]))
                addresses.append(address)
    except OSError:
        pass
    return addresses


def save():
    """Write the stack's current keys to the file. Returns how many."""
    count, keys = btclassic.link_keys()
    with open(KEY_FILE, "w") as f:
        for address, key, key_type in keys:
            f.write("%s %s %d\n" % (address.hex(), key.hex(), key_type))
    return len(keys)


def notifications():
    """How many new keys the stack has received since power on."""
    return btclassic.link_keys()[0]
