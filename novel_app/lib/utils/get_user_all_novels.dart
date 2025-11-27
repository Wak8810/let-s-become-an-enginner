import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:novel_app/models/novel.dart';

class GetUserAllNovels {
  // static Future<List<Novel>> fetchNovels() async {
  //   await Future.delayed(const Duration(seconds: 1));

  //   final String dummyNovelsJson = """
  //     [
  //       {
  //         "novel_id": "dummy_id_1",
  //         "title": "短縮ダミー小説 1",
  //         "overall_plot": "プロット1",
  //         "text_length": 1000,
  //         "created_at": "2025-11-15T10:00:00Z"
  //       },
  //       {
  //         "novel_id": "dummy_id_2",
  //         "title": "短縮ダミー小説 2",
  //         "overall_plot": "プロット2",
  //         "text_length": 2000,
  //         "created_at": "2025-11-15T14:30:00Z"
  //       }
  //     ]
  //   """;

  //   final List<dynamic> decodedJson = json.decode(dummyNovelsJson);
  //   return decodedJson.map((json) => Novel.fromJson(json as Map<String, dynamic>)).toList();
  // }

  static Future<List<Novel>> fetchNovels() async {
    final response = await http.get(Uri.parse('http://127.0.0.1:5000/novels/'));

    if (response.statusCode == 200) {
      final List<dynamic> decodedJson = json.decode(utf8.decode(response.bodyBytes));
      return decodedJson.map((json) => Novel.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load novels');
    }
  }
}