import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:novel_app/models/novel.dart';

const String _apiBaseUrl = 'http://10.0.2.2:5000'; // Androidエミュレータでの起動用
// const String _apiBaseUrl = 'http://172.0.0.1:5000'; //Web上での起動用

class GetUserAllNovels {
  static Future<List<Novel>> fetchNovels(String userId) async {
    final response = await http.get(Uri.parse('$_apiBaseUrl/users/$userId/novels'));

    if (response.statusCode == 200) {
      final List<dynamic> decodedJson = json.decode(utf8.decode(response.bodyBytes));
      return decodedJson.map((json) => Novel.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load novels');
    }
  }
}