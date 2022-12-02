import random

BASIS = ['Z', 'X']  # |0>|1> = Z-Basis; |+>|-> = X-Basis

def random_basis(key_size):
    basis = ""
    for kl in range(key_size):
        basis += random.choice(BASIS)
    return basis

def basis_check(node1_measured_bits, node1_basis, node2_basis):
    sifted_key = []
    for i in range(len(node1_measured_bits)):
        if node1_basis[i] == node2_basis[i]:
            sifted_key.append(node1_measured_bits[i].value)
    return sifted_key