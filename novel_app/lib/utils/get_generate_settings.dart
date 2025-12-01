import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/genre.dart';

const String _apiBaseUrl = 'http://10.0.2.2:5000'; // Androidエミュレータでの起動用
// const String _apiBaseUrl = 'http://172.0.0.1:5000'; //Web上での起動用

Future<List<GenreData>> fetchGenreData() async {
  final url = Uri.parse('$_apiBaseUrl/genres/');
  final response = await http.get(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final List<dynamic> decodedJson = jsonDecode(response.body);
    final List<GenreData> genreList = decodedJson
        .map((e) => GenreData.fromJson(e))
        .toList();
    return genreList;
  } else {
    final error = jsonDecode(response.body);
    throw Exception(error["message"]);
  }
}
