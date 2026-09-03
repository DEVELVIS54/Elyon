// CLIPBOARD LAN - Tests Protocol
// CHEMIN: android/test/protocol_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:android/models/protocol.dart';
void main() {
  group('Protocol', () {
    test('createHello contient les bons champs', () {
      final msg = Protocol.createHello(
        deviceId: 'android-1',
        deviceName: 'Mon Téléphone',
        publicKey: 'KEY123',
      );

      expect(msg.type, 'HELLO');
      expect(msg.deviceId, 'android-1');
      expect(msg.data['device_name'], 'Mon Téléphone');
      expect(msg.data['public_key'], 'KEY123');
    });

    test('createSync contient le contenu', () {
      final msg = Protocol.createSync(deviceId: 'android-1', content: 'Hello World');

      expect(msg.type, 'SYNC');
      expect(msg.content, 'Hello World');
      expect(msg.contentType, 'text/plain');
    });

    test('toJson / fromJson round-trip', () {
      final original = Protocol.createSync(deviceId: 'dev1', content: 'Test content');
      final jsonStr = original.toJson();
      final parsed = ProtocolMessage.fromJson(jsonStr);

      expect(parsed, isNotNull);
      expect(parsed!.type, 'SYNC');
      expect(parsed.content, 'Test content');
    });

    test('fromJson retourne null sur JSON invalide', () {
      final parsed = ProtocolMessage.fromJson('{invalid json}');
      expect(parsed, isNull);
    });

    test('validate rejette un message sans type', () {
      final msg = ProtocolMessage({'timestamp': 'now'});
      final (valid, reason) = Protocol.validate(msg);

      expect(valid, isFalse);
      expect(reason.toLowerCase(), contains('type'));
    });

    test('validate rejette un SYNC sans content', () {
      final msg = ProtocolMessage({'type': 'SYNC', 'device_id': 'dev1'});
      final (valid, reason) = Protocol.validate(msg);

      expect(valid, isFalse);
      expect(reason.toLowerCase(), contains('content'));
    });

    test('validate accepte un SYNC valide', () {
      final msg = Protocol.createSync(deviceId: 'dev1', content: 'ok');
      final (valid, _) = Protocol.validate(msg);

      expect(valid, isTrue);
    });

    test('createPing / createPong ont le bon type', () {
      expect(Protocol.createPing().type, 'PING');
      expect(Protocol.createPong().type, 'PONG');
    });
  });
}