from netqasm.logging.output import get_new_app_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from epr_socket import DerivedEPRSocket as EPRSocket

from util import random_basis, basis_check

def main(app_config=None, key_length=16):
    app_logger = get_new_app_logger(app_name=app_config.app_name,
                                    log_config=app_config.log_config)
    app_logger.log("Bob is alive")

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
        for base in bob_basis:
            # Create an entangled pair using the EPR socket to bob
            q_ent = epr_socket.recv()[0]
            app_logger.log("Entanglement pair creation at bob")

            if base == 'X':
                q_ent.H()

            m = q_ent.measure()

            bob.flush()

            bob_measured_bits.append(m)
            app_logger.log(f"Bob is measuring with {base} base: {m}")

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
