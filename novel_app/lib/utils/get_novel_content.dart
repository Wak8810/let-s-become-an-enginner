import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:novel_app/models/novel_content.dart';

class GetNovelContent {
  static Future<NovelContent> fetchNovelContent(String novelId) async {
    final response = await http.get(
      Uri.parse('http://10.0.2.2:5000/novels/$novelId/contents'),
      // Uri.parse('http://localhost:5000/novels/$novelId/contents'),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return NovelContent.fromJson(jsonDecode(decodedBody));
    } else {
      throw Exception('Failed to load novel content');
    }
  }
}
