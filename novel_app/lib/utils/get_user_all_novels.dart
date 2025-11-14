import 'dart:convert';

class GetUserAllNovels {
  static Future<List<Map<String, dynamic>>> fetchNovels() async {
    await Future.delayed(const Duration(seconds: 1));

    final String dummyNovelsJson = """
      [
        {
          "title": "普通の小説",
          "content": "普通の内容",
          "created_at": "2025-11-15T10:00:00Z"
        },
        {
          "title": "短",
          "content": "短",
          "created_at": "2025-11-15T14:30:00Z"
        },
        {
          "title": "長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説長い小説",
          "content": "長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容長い内容",
          "created_at": "2025-11-15T08:45:00Z"
        }
      ]
    """;

    final List<dynamic> decodedJson = json.decode(dummyNovelsJson);
    return decodedJson.cast<Map<String, dynamic>>();
  }
}