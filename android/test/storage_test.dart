// CLIPBOARD LAN - Tests Storage Service
// CHEMIN: android/test/storage_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:android/services/storage_service.dart';
import 'package:android/models/device.dart';
import 'package:android/models/history_item.dart';

void main() {
  group('StorageService', () {
    late StorageService storage;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      storage = StorageService();
      await storage.init();
    });

    test('Sauvegarde, consultation et suppression d\'un appareil', () async {
      final device = Device(
        deviceId: 'win-123',
        deviceName: 'PC Bureau',
        deviceType: 'windows',
        isTrusted: false,
        lastSeen: DateTime.now(),
        createdAt: DateTime.now(),
        ipAddress: '192.168.1.10',
        port: 7777,
      );

      await storage.saveDevice(device);
      var devices = await storage.getDevices();
      expect(devices.length, equals(1));
      expect(devices.first.deviceId, equals('win-123'));
      expect(devices.first.isTrusted, isFalse);

      // Approbation
      await storage.setDeviceTrust('win-123', true);
      devices = await storage.getDevices();
      expect(devices.first.isTrusted, isTrue);

      // Suppression
      await storage.deleteDevice('win-123');
      devices = await storage.getDevices();
      expect(devices.isEmpty, isTrue);
    });

    test('Ajout, consultation et suppression dans l\'historique', () async {
      final item1 = HistoryItem(
        id: '1',
        content: 'Premier texte copié',
        sourceDevice: 'Android',
        createdAt: DateTime.now(),
      );
      final item2 = HistoryItem(
        id: '2',
        content: 'Deuxième texte copié',
        sourceDevice: 'Windows',
        createdAt: DateTime.now(),
      );

      await storage.addHistoryItem(item1);
      await storage.addHistoryItem(item2);

      var history = await storage.getHistory();
      expect(history.length, equals(2));
      expect(history.first.content, equals('Deuxième texte copié')); // Plus récent en premier

      // Suppression d'un élément
      await storage.deleteHistoryItem('2');
      history = await storage.getHistory();
      expect(history.length, equals(1));
      expect(history.first.id, equals('1'));

      // Vidage complet
      await storage.clearHistory();
      history = await storage.getHistory();
      expect(history.isEmpty, isTrue);
    });

    test('Respect de la limite maximale d\'éléments dans l\'historique', () async {
      await storage.setMaxHistoryItems(3);

      for (int i = 0; i < 5; i++) {
        await storage.addHistoryItem(HistoryItem(
          id: '$i',
          content: 'Contenu unique $i',
          sourceDevice: 'Android',
          createdAt: DateTime.now(),
        ));
      }

      final history = await storage.getHistory();
      expect(history.length, equals(3));
      expect(history.first.content, equals('Contenu unique 4'));
    });

    test('Gestion des paramètres (settings)', () async {
      expect(storage.isHistoryEnabled, isTrue);

      await storage.setHistoryEnabled(false);
      expect(storage.isHistoryEnabled, isFalse);

      await storage.setLastHost('192.168.1.50');
      expect(storage.lastHost, equals('192.168.1.50'));

      await storage.setLastPort(8888);
      expect(storage.lastPort, equals(8888));
    });
  });
}
