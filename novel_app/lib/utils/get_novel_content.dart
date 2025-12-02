import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:novel_app/models/novel_content.dart';
import './api_config.dart';

class GetNovelContent {
  static Future<NovelContent> fetchNovelContent(
      String novelId, String userId) async {
    final response = await http.get(
      Uri.parse('$apiBaseUrl/novels/$novelId/text'),
      headers: {
        'X-User-ID': userId,
      },
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      final Map<String, dynamic> json = jsonDecode(decodedBody);
      return NovelContent.fromJson(json);
    } else {
      throw Exception('Failed to load novel content');
    }
  }
}
