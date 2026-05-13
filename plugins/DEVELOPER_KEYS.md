# Developer Public Key Storage

This document specifies how developers store and manage their Ed25519 public keys for plugin signing.

## Key Generation

Developers must generate an Ed25519 keypair for signing plugins:

```bash
# Generate private key
openssl genpkey -algorithm ED25519 -out private_key.pem

# Extract public key
openssl pkey -in private_key.pem -pubout -out developer_id_ed25519.pub
```

## Key Storage Structure

Each developer repository must maintain the following structure:

```
your-plugin-repo/
├── .keys/
│   └── {developer_id}_ed25519.pub    # Public key for signature verification
├── your-plugin-1.0.0.astrplug
└── your-plugin-1.0.0.signature
```

## Developer ID

The developer_id is a UUID v4 assigned when the developer registers on the marketplace. It must:
- Be globally unique
- Be persistent across plugin updates
- Match the author_id in plugin manifest.json

## Public Key File Format

The public key file must:
- Be named: `{developer_id}_ed25519.pub`
- Contain the raw Ed25519 public key in PEM format
- Be committed to the root of the plugin repository
- Be accessible via raw GitHub URL

Example:
```
# Content of 550e8400-e29b-41d4-a716-446655440000_ed25519.pub
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9...d3A+EPa5OBQ=
-----END PUBLIC KEY-----
```

## Key Rotation

If a key needs to be rotated:
1. Generate a new keypair
2. Update all plugins with new signatures
3. Submit key rotation request to marketplace admins
4. Old signatures will be rejected after rotation period

## Signature Verification

The marketplace verifies signatures using:

```bash
# Developer signs the plugin
openssl dgst -sha256 -sign private_key.pem plugin.astrplug > plugin.signature

# Marketplace verifies (using public key from .keys directory)
openssl dgst -sha256 -verify developer_id_ed25519.pub \
  -signature plugin.signature plugin.astrplug
```

## Security Best Practices

1. **Never commit private keys** to any repository
2. **Backup private keys securely** (hardware security module recommended)
3. **Use strong passphrases** if supported by your key storage
4. **Rotate keys periodically** (recommended: annually)
5. **Monitor key usage** for suspicious activity
