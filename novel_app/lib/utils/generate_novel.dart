import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/novel.dart';
import '../models/generated_novel.dart';

Future<GeneratedNovel> fetchGeneratedNovel(
  String ideal_text_length,
  String genre,
  String style,
) async {
  final url = Uri.parse('http://localhost:5000/novels/init');
  final novelData = {
    "user_id": "e116fe527f714ba4a34f512f29196ac2", //現状手動で設定
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
