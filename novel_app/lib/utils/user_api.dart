import 'dart:convert';
import 'package:http/http.dart' as http;
import './api_config.dart';
import 'package:novel_app/models/user.dart';

Future<User> registerUser() async {
  final response = await http.post(
    Uri.parse('$apiBaseUrl/users/'),
  );

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return User.fromJson(data);
  } else {
    throw Exception('Failed to register user');
  }
}
