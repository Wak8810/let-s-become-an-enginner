import 'package:http/http.dart' as http;
import 'dart:convert';
import './api_config.dart';
import '../models/mood.dart';

Future<List<MoodData>> fetchMoodData() async {
  final url = Uri.parse('$apiBaseUrl/moods/');
  final response = await http.get(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final List<dynamic> decodedJson = jsonDecode(response.body);
    final List<MoodData> genreList = decodedJson
        .map((e) => MoodData.fromJson(e))
        .toList();
    return genreList;
  } else {
    final error = jsonDecode(response.body);
    throw Exception(error["message"]);
  }
}
