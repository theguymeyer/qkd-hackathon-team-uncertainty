from netqasm.logging.output import get_new_app_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from epr_socket import DerivedEPRSocket as EPRSocket

from util import random_basis, basis_check

def main(app_config=None, key_length=16):

    app_logger = get_new_app_logger(app_name=app_config.app_name,
                                    log_config=app_config.log_config)
    app_logger.log("Alice is alive")

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
        app_logger.log("Alice starts the protocol")
        secret_key = []

        alice_measured_bits = []
        for basis in alice_basis:
            # Create an entangled pair using the EPR socket to bob
            q_ent = epr_socket.create()[0]
            app_logger.log("Entanglement pair creation at alice")

            if basis == 'X':
                q_ent.H()
                
            m = q_ent.measure()

            alice.flush()

            alice_measured_bits.append(m)
            app_logger.log(f"Alice is measuring with X base: {m}")


        # Send classical information using socket to bob
        socket.send(alice_basis)
        app_logger.log("Alice send her basis to Bob")

        # Receive bob basis using socket from bob
        app_logger.log("Alice is waiting bob's basis")
        bob_basis = socket.recv()

        sk = basis_check(alice_measured_bits, alice_basis, bob_basis)
        app_logger.log(f"Alice compute the sifted key: {sk}")

    # RETURN THE SECRET KEY HERE
    return {
        "secret_key": sk,
    }


if __name__ == "__main__":
    main()
