// CLIPBOARD LAN - Tests Anti-Loop Service
// CHEMIN: android/test/anti_loop_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:android/services/anti_loop_service.dart';

void main() {
  group('AntiLoopService', () {
    late AntiLoopService service;

    setUp(() {
      service = AntiLoopService(maxSize: 5, timeoutSeconds: 2);
    });

    test('sha256Content génère une empreinte correcte', () {
      final hash1 = service.sha256Content('Bonjour le monde');
      final hash2 = service.sha256Content('Bonjour le monde');
      final hash3 = service.sha256Content('Autre texte');

      expect(hash1, equals(hash2));
      expect(hash1, isNot(equals(hash3)));
      expect(hash1.length, equals(64));
    });

    test('add et isLoopDetected fonctionnent comme prévu', () {
      expect(service.isLoopDetected('Hello'), isFalse);

      service.add('Hello', 'source1');

      expect(service.isLoopDetected('Hello'), isTrue);
      expect(service.isLoopDetected('Different'), isFalse);
    });

    test('shouldSync autorise le premier envoi et bloque les doublons', () {
      final (allow1, reason1) = service.shouldSync('Mon code secret', 'local');
      expect(allow1, isTrue);

      service.add('Mon code secret', 'local');

      final (allow2, reason2) = service.shouldSync('Mon code secret', 'local');
      expect(allow2, isFalse);
      expect(reason2, contains('Doublon'));

      final (allow3, reason3) = service.shouldSync('Mon code secret', 'remote');
      expect(allow3, isFalse);
      expect(reason3, contains('Écho'));
    });

    test('trimCache respecte la taille maximale (FIFO)', () {
      for (int i = 0; i < 10; i++) {
        service.add('Texte $i', 'local');
      }

      expect(service.count, lessThanOrEqualTo(5));
      // Les premiers devraient avoir été évincés
      expect(service.isLoopDetected('Texte 0'), isFalse);
      // Les plus récents doivent être présents
      expect(service.isLoopDetected('Texte 9'), isTrue);
    });

    test('clear vide entièrement le cache', () {
      service.add('Texte A', 'local');
      service.add('Texte B', 'local');
      expect(service.count, equals(2));

      service.clear();
      expect(service.count, equals(0));
      expect(service.isLoopDetected('Texte A'), isFalse);
    });
  });
}
