from netqasm.logging.glob import get_netqasm_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from epr_socket import DerivedEPRSocket as EPRSocket
from common import log
import random

BASIS = ['Z', 'X']  # |0>|1> = Z-Basis; |+>|-> = X-Basis

logger = get_netqasm_logger()

def random_basis(key_size):
    bob_basis = ""
    for kl in range(key_size):
        bob_basis += random.choice(BASIS)
    return bob_basis

def basis_check(bob_measured_bits, alice_basis, bob_basis):
    sifted_key = []
    for i in range(len(bob_measured_bits)):
        if alice_basis[i] == bob_basis[i]:
            sifted_key.append(bob_measured_bits)
    return sifted_key


def main(app_config=None, key_length=16):
    log("my name is bob", "bob", app_config)

    # Socket for classical communication
    socket = Socket("bob", "alice", log_config=app_config.log_config)
    # Socket for EPR generation
    epr_socket = EPRSocket("alice")

    bob = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )

    bob_basis = random_basis(key_length)
    with bob:
        secret_key = []
        
        bob_measured_bits = []
        for basis in bob_basis:
            # Create an entangled pair using the EPR socket to bob
            q_ent = epr_socket.recv()[0]
            logger.info("Entanglement pair creation at bob")

            if basis == 'Z':
                bob_measured_bits.append(q_ent.measure())
                logger.info("bob measures with Z base")

            if basis == 'X':
                q_ent.H()
                bob_measured_bits.append(q_ent.measure())
                logger.info("bob measures with Z base")
        
        # Receive alice basis
        alice_basis = socket.recv()

        # Send bob basis using socket to alice
        socket.send(bob_basis)

        sk = basis_check(bob_measured_bits, alice_basis, bob_basis)


    # RETURN THE SECRET KEY HERE
    return {
        "secret_key": sk,
    }


if __name__ == "__main__":
    main()
