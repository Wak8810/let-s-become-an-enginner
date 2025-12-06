import 'package:http/http.dart' as http;
import 'dart:convert';
import './api_config.dart';
import '../models/generated_novel.dart';

Future<GeneratedNovel> fetchGeneratedNovel(
  String ideal_text_length,
  String genre,
  String style,
  String userId,
  String mood,
) async {
  final url = Uri.parse('$apiBaseUrl/novels/init');
  final novelData = {
    "user_id": userId,
    "novel_setting": {
      "ideal_text_length": int.parse(ideal_text_length),
      "genre": genre,
      "style": style,
      "mood":mood
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
