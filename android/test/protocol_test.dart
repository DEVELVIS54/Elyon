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

    test('createSync contient le contenu et signature optionnelle', () {
      final msg = Protocol.createSync(
        deviceId: 'android-1',
        content: 'Hello World',
        signature: 'SIG456',
      );

      expect(msg.type, 'SYNC');
      expect(msg.content, 'Hello World');
      expect(msg.contentType, 'text/plain');
      expect(msg.signature, 'SIG456');
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

    test('createAck contient message_id', () {
      final ack = Protocol.createAck(messageId: 'msg-999');
      expect(ack.type, 'ACK');
      expect(ack.messageId, 'msg-999');
    });

    test('createPair et createAuth génèrent des messages valides', () {
      final pair = Protocol.createPair(
        deviceId: 'dev1',
        deviceName: 'Mobile',
        publicKey: 'PUBKEY',
      );
      expect(pair.type, 'PAIR');
      expect(pair.deviceId, 'dev1');

      final auth = Protocol.createAuth(deviceId: 'dev1', challengeResponse: 'TOKEN123');
      expect(auth.type, 'AUTH');
      expect(auth.data['auth_token'], 'TOKEN123');
    });
  });
}