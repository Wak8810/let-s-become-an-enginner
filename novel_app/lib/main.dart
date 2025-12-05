import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:novel_app/screens/novel_list/novel_list_screen.dart';
import 'package:novel_app/utils/user_api.dart';
import 'package:provider/provider.dart';

final RouteObserver<PageRoute> routeObserver = RouteObserver<PageRoute>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const storage = FlutterSecureStorage();
  String? userId = await storage.read(key: 'user_id');
  if (userId == null || userId.isEmpty) {
    final newUser = await registerUser();
    userId = newUser.id;
    await storage.write(key: 'user_id', value: userId);
  }
  runApp(Provider<String>.value(value: userId, child: const MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Novel App',
      theme: ThemeData(
        colorScheme: const ColorScheme.light(
          primary: Colors.black,
          secondary: Colors.black,
          surface: Colors.white,
          background: Colors.white,
          onPrimary: Colors.white,
          onSurface: Colors.black,
        ),
        useMaterial3: true,
      ),
      navigatorObservers: [routeObserver],
      home: const NovelListScreen(),
    );
  }
}
