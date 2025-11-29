import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:novel_app/screens/novel_list/novel_list_screen.dart';
import 'package:novel_app/utils/user_api.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const storage = FlutterSecureStorage();
  String? userId = await storage.read(key: 'user_id');
  if (userId == null || userId.isEmpty) {
    final newUser = await registerUser();
    userId = newUser.id;
    await storage.write(key: 'user_id', value: userId);
  }
  runApp(MyApp(userId: userId));
}



class MyApp extends StatelessWidget {
  const MyApp({super.key, required this.userId});
  final String userId;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Novel App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: NovelListScreen(userId: userId),
    );
  }
}
