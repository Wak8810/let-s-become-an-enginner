import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:novel_app/models/user.dart'; // Import the User model

const String _apiBaseUrl = 'http://10.0.2.2:5000'; // Androidエミュレータでの起動用
// const String _apiBaseUrl = 'http://172.0.0.1:5000'; //Web上での起動用

Future<User> registerUser() async {
  final response = await http.post(
    Uri.parse('$_apiBaseUrl/users/'),
  );

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return User.fromJson(data); // Return User object
  } else {
    throw Exception('Failed to register user');
  }
}
