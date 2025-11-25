import 'package:http/http.dart' as http;
import 'dart:convert';

Future<String> fetchApiData() async {
  final url = Uri.parse('http://localhost:5000/novels/init');
  final novelData = {
    "user_id": "e116fe527f714ba4a34f512f29196ac2",
    "novel_setting": {
      "ideal_text_length": 400,
      "genre": "sf",
      "style": "三人称",
    }
  };
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: json.encode(novelData),
    );

  if (response.statusCode == 200) {
    final response_json = json.decode(response.body);
    return response_json["title"];
  } else {
    return 'エラー: ${response.statusCode}';
  }
}
