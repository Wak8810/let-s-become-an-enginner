import 'dart:convert';
import 'package:http/http.dart' as http;
import './api_config.dart';
import 'package:novel_app/models/novel.dart';

class GetUserAllNovels {
  static Future<List<Novel>> fetchNovels(String userId) async {
    final response = await http.get(Uri.parse('$apiBaseUrl/users/$userId/novels'));

    if (response.statusCode == 200) {
      final List<dynamic> decodedJson = json.decode(utf8.decode(response.bodyBytes));
      return decodedJson.map((json) => Novel.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load novels');
    }
  }
}