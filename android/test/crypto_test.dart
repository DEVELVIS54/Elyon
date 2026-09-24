// CLIPBOARD LAN - Tests Crypto Service
// CHEMIN: android/test/crypto_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:android/services/crypto_service.dart';

void main() {
  group('CryptoService', () {
    late CryptoService crypto;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      crypto = CryptoService();
      await crypto.init();
    });

    test('Initialise un identifiant unique et une clé publique', () {
      expect(crypto.deviceId, startsWith('android-'));
      expect(crypto.publicKeyPem, contains('BEGIN PUBLIC KEY'));
      expect(crypto.hmacSecret, isNotEmpty);
    });

    test('hmacSign et hmacVerify valident les messages authentiques', () {
      const message = 'Test de synchronisation sécurisée';
      final signature = crypto.hmacSign(message);

      expect(signature, isNotEmpty);
      expect(crypto.hmacVerify(message, signature), isTrue);
      expect(crypto.hmacVerify('Message altéré', signature), isFalse);
    });

    test('getFingerprint retourne une empreinte hexadécimale formatée', () {
      final fingerprint = crypto.getFingerprint(crypto.publicKeyPem);

      expect(fingerprint, isNotEmpty);
      expect(fingerprint, contains(':'));
      expect(fingerprint.split(':').length, greaterThanOrEqualTo(8));
    });

    test('Identité persistante après réinitialisation', () async {
      final initialId = crypto.deviceId;
      final initialKey = crypto.publicKeyPem;

      // Nouvelle instance avec le même SharedPreferences mock
      final crypto2 = CryptoService();
      await crypto2.init();

      expect(crypto2.deviceId, equals(initialId));
      expect(crypto2.publicKeyPem, equals(initialKey));
    });
  });
}
