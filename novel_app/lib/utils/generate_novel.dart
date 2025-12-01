import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/novel.dart';
import '../models/generated_novel.dart';

const String _apiBaseUrl = 'http://10.0.2.2:5000'; // Androidエミュレータでの起動用
// const String _apiBaseUrl = 'http://172.0.0.1:5000'; //Web上での起動用

Future<GeneratedNovel> fetchGeneratedNovel(
  String ideal_text_length,
  String genre,
  String style,
  String userId,
) async {
  final url = Uri.parse('$_apiBaseUrl/novels/init');
  final novelData = {
    "user_id": userId,
    "novel_setting": {
      "ideal_text_length": int.parse(ideal_text_length),
      "genre": genre,
      "style": style,
    },
  };
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: json.encode(novelData),
  );

  if (response.statusCode == 200) {
    final response_json = json.decode(response.body);
    GeneratedNovel generatedNovel = GeneratedNovel.fromJson(response_json);
    return generatedNovel;
  } else {
    final error = jsonDecode(response.body);
    throw Exception(error["message"]);
  }
}
