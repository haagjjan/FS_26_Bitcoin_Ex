# Problem 3

Source: [`Problem Set 2026-1.pdf`](../docs/Problem%20Set%202026-1.pdf)

In this problem, we use the RSA algorithm covered in the lecture on asymmetric
cryptography to create a private and public key and to send an encrypted message
similar to the example in the lecture. We use the parameters `p = 13`,
`q = 29`, and `e = 5` to encipher the message `L`.

## Problem 3.1

Compute the number `N` and convert the message `M = L` using the ASCII table
into a decimal number. Subsequently, encrypt this decimal number to receive the
encrypted message `C`.

Note: Conventional calculators might not be able to handle numbers of this size
well. The problem sheet recommends the online modulo calculator at
<https://planetcalc.com/8326/>.

## Problem 3.2

Compute the number `phi(N)` and derive the private key `k_p`, which will be used
to decrypt the message `C`.

Hint: To find the multiplicative inverse in modulo calculations, use the
Euclidean Algorithm. There are several online tools that can be used instead of
doing this by hand, for example <https://planetcalc.com/3311/>.

## Problem 3.3

Decrypt the encrypted message `C` using the private key `k_p` and check the
result with the original message `M = L`.
