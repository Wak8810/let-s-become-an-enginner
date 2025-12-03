import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;

String get apiBaseUrl {
  if (kIsWeb) {
    return 'http://127.0.0.1:5000';
  }

  if (Platform.isAndroid) {
    return 'http://10.0.2.2:5000';
  }
  
  // 上記以外（iOS, macOS, Windows, Linux）の場合
  return 'http://127.0.0.1:5000';
}
