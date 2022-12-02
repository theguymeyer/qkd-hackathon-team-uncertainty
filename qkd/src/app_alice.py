from netqasm.logging.glob import get_netqasm_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from epr_socket import DerivedEPRSocket as EPRSocket
from common import log

import random

BASIS = ['Z', 'X']  # |0>|1> = Z-Basis; |+>|-> = X-Basis

logger = get_netqasm_logger()

def random_basis(key_size):
    alice_basis = ""
    for kl in range(key_size):
        alice_basis += random.choice(BASIS)
    return alice_basis

def basis_check(alice_measured_bits, alice_basis, bob_basis):
    sifted_key = []
    for i in range(len(alice_measured_bits)):
        if alice_basis[i] == bob_basis[i]:
            sifted_key.append(alice_measured_bits)
    return sifted_key

def main(app_config=None, key_length=16):

    log("test 1", app_config)
    log("test 2", app_config)

    # Socket for classical communication
    socket = Socket("alice", "bob", log_config=app_config.log_config)
    # Socket for EPR generation
    epr_socket = EPRSocket("bob")

    alice = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )

    alice_basis = random_basis(key_length)
    
    with alice:
        secret_key = []

        alice_measured_bits = []
        for basis in alice_basis:
            # Create an entangled pair using the EPR socket to bob
            q_ent = epr_socket.create()[0]
            logger.info("Entanglement pair creation at alice")

            if basis == 'Z':
                alice_measured_bits.append(q_ent.measure())
                logger.info("Alice measures with Z base")

            elif basis == 'X':
                q_ent.H()
                alice_measured_bits.append(q_ent.measure())
                logger.info("Alice measures with Z base")
        
        # Send classical information using socket to bob
        socket.send(alice_basis)

        # # Receive bob basis using socket from bob
        bob_basis = socket.recv()

        sk = basis_check(alice_measured_bits, alice_basis, bob_basis)

    # RETURN THE SECRET KEY HERE
    return {
        "secret_key": sk,
    }


if __name__ == "__main__":
    main()
