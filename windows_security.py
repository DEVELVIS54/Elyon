"""
CLIPBOARD LAN - Module Sécurité
Gestion RSA-2048, HMAC-SHA256, génération/chargement clés.

PHASE 1: Crypto core
"""

import os
import hashlib
import hmac
import json
from pathlib import Path
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class SecurityManager:
    """Gère la cryptographie RSA et HMAC pour Clipboard LAN."""
    
    def __init__(self, keys_dir: Path, key_size: int = 2048):
        """
        Initialise le gestionnaire de sécurité.
        
        Args:
            keys_dir: Dossier contenant les clés RSA
            key_size: Taille des clés RSA (2048, 3072, 4096)
        """
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.key_size = key_size
        
        self.private_key_path = self.keys_dir / "private.pem"
        self.public_key_path = self.keys_dir / "public.pem"
        self.hmac_secret_path = self.keys_dir / "hmac.secret"
        
        # Charger ou créer les clés
        self._ensure_keys_exist()
    
    def _ensure_keys_exist(self):
        """Crée les clés RSA et HMAC s'il n'existent pas."""
        
        # RSA
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            print(f"🔐 Génération clés RSA-{self.key_size}...")
            self._generate_rsa_keys()
        
        # HMAC
        if not self.hmac_secret_path.exists():
            print(f"🔐 Génération secret HMAC...")
            self._generate_hmac_secret()
    
    def _generate_rsa_keys(self):
        """Génère une paire de clés RSA-2048."""
        
        # Générer la clé privée
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        
        # Sauvegarder la clé privée (non chiffrée pour MVP)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.private_key_path.write_bytes(private_pem)
        print(f"  ✓ Clé privée: {self.private_key_path}")
        
        # Sauvegarder la clé publique
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key_path.write_bytes(public_pem)
        print(f"  ✓ Clé publique: {self.public_key_path}")
    
    def _generate_hmac_secret(self):
        """Génère un secret HMAC-SHA256 (32 octets)."""
        secret = os.urandom(32)
        self.hmac_secret_path.write_bytes(secret)
        print(f"  ✓ Secret HMAC: {self.hmac_secret_path}")
    
    def get_public_key_pem(self) -> str:
        """Retourne la clé publique au format PEM (str)."""
        return self.public_key_path.read_text()
    
    def get_private_key(self):
        """Charge et retourne la clé privée RSA."""
        private_pem = self.private_key_path.read_bytes()
        return serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
    
    def get_public_key_from_pem(self, pem_string: str):
        """Charge une clé publique depuis une string PEM."""
        public_pem = pem_string.encode('utf-8')
        return serialization.load_pem_public_key(
            public_pem,
            backend=default_backend()
        )
    
    # ========================================================================
    # RSA : Chiffrement & Déchiffrement
    # ========================================================================
    
    def rsa_encrypt(self, plaintext: str, public_key_pem: str) -> str:
        """
        Chiffre un texte avec la clé publique RSA.
        
        Args:
            plaintext: Texte à chiffrer
            public_key_pem: Clé publique en format PEM
        
        Returns:
            Données chiffrées en Base64
        """
        import base64
        
        public_key = self.get_public_key_from_pem(public_key_pem)
        ciphertext = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def rsa_decrypt(self, ciphertext_b64: str) -> str:
        """
        Déchiffre un texte avec la clé privée RSA.
        
        Args:
            ciphertext_b64: Données chiffrées en Base64
        
        Returns:
            Texte déchiffré
        """
        import base64
        
        private_key = self.get_private_key()
        ciphertext = base64.b64decode(ciphertext_b64.encode('utf-8'))
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode('utf-8')
    
    # ========================================================================
    # RSA : Signature (authentification)
    # ========================================================================
    
    def rsa_sign(self, message: str) -> str:
        """
        Signe un message avec la clé privée RSA.
        
        Args:
            message: Message à signer
        
        Returns:
            Signature en Base64
        """
        import base64
        
        private_key = self.get_private_key()
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def rsa_verify(self, message: str, signature_b64: str, public_key_pem: str) -> bool:
        """
        Vérifie une signature RSA.
        
        Args:
            message: Message original
            signature_b64: Signature en Base64
            public_key_pem: Clé publique en format PEM
        
        Returns:
            True si signature valide, False sinon
        """
        import base64
        
        try:
            public_key = self.get_public_key_from_pem(public_key_pem)
            signature = base64.b64decode(signature_b64.encode('utf-8'))
            public_key.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    # ========================================================================
    # HMAC : Authentification de message
    # ========================================================================
    
    def get_hmac_secret(self) -> bytes:
        """Charge et retourne le secret HMAC."""
        return self.hmac_secret_path.read_bytes()
    
    def hmac_sign(self, message: str) -> str:
        """
        Crée une signature HMAC-SHA256 d'un message.
        
        Args:
            message: Message à signer
        
        Returns:
            Signature HMAC en hexadécimal
        """
        secret = self.get_hmac_secret()
        signature = hmac.new(
            secret,
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return signature.hex()
    
    def hmac_verify(self, message: str, signature_hex: str) -> bool:
        """
        Vérifie une signature HMAC-SHA256.
        
        Args:
            message: Message original
            signature_hex: Signature HMAC en hexadécimal
        
        Returns:
            True si signature valide, False sinon
        """
        expected_signature = self.hmac_sign(message)
        return hmac.compare_digest(expected_signature, signature_hex)
    
    # ========================================================================
    # Utilitaires
    # ========================================================================
    
    def sha256(self, data: str) -> str:
        """Calcule le hash SHA256 d'une string."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def get_key_info(self) -> dict:
        """Retourne les infos sur les clés (pour debug)."""
        private_key = self.get_private_key()
        public_key = private_key.public_key()
        
        return {
            "rsa_key_size": self.key_size,
            "private_key_path": str(self.private_key_path),
            "public_key_path": str(self.public_key_path),
            "hmac_secret_path": str(self.hmac_secret_path),
            "public_key_fingerprint": self.sha256(self.get_public_key_pem())[:16],
        }


# ============================================================================
# Tests locaux
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("🧪 Tests du module Security\n")
    
    # Créer un gestionnaire de sécurité avec dossier temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        sec = SecurityManager(Path(tmpdir))
        
        # 1. RSA Encryption/Decryption
        print("1️⃣  Test RSA Encryption/Decryption")
        plaintext = "Hello, Clipboard LAN!"
        encrypted = sec.rsa_encrypt(plaintext, sec.get_public_key_pem())
        decrypted = sec.rsa_decrypt(encrypted)
        assert decrypted == plaintext, "RSA decrypt failed!"
        print(f"  ✓ Plaintext: {plaintext}")
        print(f"  ✓ Encrypted: {encrypted[:50]}...")
        print(f"  ✓ Decrypted: {decrypted}\n")
        
        # 2. RSA Signature
        print("2️⃣  Test RSA Signature/Verification")
        message = "Device authentication"
        signature = sec.rsa_sign(message)
        is_valid = sec.rsa_verify(message, signature, sec.get_public_key_pem())
        assert is_valid, "RSA signature verification failed!"
        print(f"  ✓ Message: {message}")
        print(f"  ✓ Signature: {signature[:50]}...")
        print(f"  ✓ Verification: {is_valid}\n")
        
        # 3. HMAC Sign/Verify
        print("3️⃣  Test HMAC Sign/Verification")
        msg = '{"type":"SYNC","content":"test"}'
        hmac_sig = sec.hmac_sign(msg)
        is_valid_hmac = sec.hmac_verify(msg, hmac_sig)
        assert is_valid_hmac, "HMAC verification failed!"
        print(f"  ✓ Message: {msg}")
        print(f"  ✓ HMAC: {hmac_sig}")
        print(f"  ✓ Verification: {is_valid_hmac}\n")
        
        # 4. SHA256
        print("4️⃣  Test SHA256")
        test_data = "anti-loop-test"
        hash_val = sec.sha256(test_data)
        print(f"  ✓ Data: {test_data}")
        print(f"  ✓ SHA256: {hash_val}\n")
        
        # 5. Key Info
        print("5️⃣  Key Information")
        info = sec.get_key_info()
        for key, value in info.items():
            print(f"  • {key}: {value}")
        
        print("\n✅ Tous les tests de sécurité passent!")
