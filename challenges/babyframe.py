from pwn import remote
from struct import pack


def generate_space_packet(
    apid: int,
    packet_count: int,
    payload: bytes
) -> bytes:

    # CCSDS Space Packet Primary Header
    #
    # Version = 000
    # Type = 1 (Telecommand)
    # Secondary Header Flag = 0
    # APID = supplied APID

    packet_id = (1 << 12) | apid

    # Sequence flags = 11 (unsegmented)
    # Sequence count = supplied count
    seq_control = (3 << 14) | packet_count

    # CCSDS length = data field size - 1
    data_length = len(payload) - 1

    header = pack(
        ">HHH",
        packet_id,
        seq_control,
        data_length
    )

    return header + payload


def generate_tc_frame(
    spacecraft_id: int,
    virtual_channel_id: int,
    tc_packet_count: int,
    payload: bytes
) -> bytes:

    version = 0
    bypass_flag = 0
    control_command_flag = 0

    first_word = (
        (version << 14)
        | (bypass_flag << 13)
        | (control_command_flag << 12)
        | spacecraft_id
    )

    # Frame length includes the 5-byte primary header.
    frame_length = len(payload) + 5 - 1

    second_word = (
        (virtual_channel_id << 10)
        | frame_length
    )

    header = pack(
        ">HHB",
        first_word,
        second_word,
        tc_packet_count
    )

    return header + payload


def main():

    HOST = "154.57.164.82"
    PORT = 30128

    space_packet = generate_space_packet(
        apid=42,
        packet_count=0,
        payload=b"HEALTHCHECK"
    )

    frame = generate_tc_frame(
        spacecraft_id=12,
        virtual_channel_id=3,
        tc_packet_count=0,
        payload=space_packet
    )

    r = remote(HOST, PORT)

    r.send(frame)

    response = r.recv()
    print(response.decode(errors="replace"))

    r.close()


if __name__ == "__main__":
    main()
