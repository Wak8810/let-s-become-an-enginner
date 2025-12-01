import 'package:http/http.dart' as http;
import 'dart:convert';

const String _apiBaseUrl = 'http://10.0.2.2:5000'; // Androidエミュレータでの起動用
// const String _apiBaseUrl = 'http://172.0.0.1:5000'; //Web上での起動用

Future<String> fetchApiData(String userId) async {
  final url = Uri.parse('$_apiBaseUrl/novels/init');
  final novelData = {
    "user_id": userId,
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